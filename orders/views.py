from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .cart import Cart
from home.models import Product
from .forms import CartAddForm, CouponForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Coupon
import datetime
from django.urls import reverse
from djangoProject__a import settings
import json
import requests


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        return render(request, "checkout.html", {"cart": cart})


class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data["quantity"])
        return redirect("home:home")


class CartRemoveView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect("home:home")


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(
                order=order, product=item['product'], price=item['price'], quantity=item['quantity']
            )
        cart.clear()
        return redirect('orders:order_detail', order.id)


class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponForm

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, "chekedout.html", {"order": order, "form": self.form_class})


class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponForm

    def post(self, request, order_id):
        now = datetime.datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(
                    code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(
                    request, 'this coupon does not exists', 'danger')
                return redirect('orders:order_detail', order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
            messages.error(request, 'it worked', 'success')
        return redirect('orders:order_detail', order_id)


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
CallbackURL = reverse('orders:order_verify')


class OrderPayView(LoginRequiredMixin, View):
    def get(request, order_id):
        order = Order.objects.get(id=order_id)
        request.session['order'] = {'order_id': order_id}
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.get_total_price(),
            "Description": description,
            "Phone": order.user.phone_number,
            "CallbackURL": CallbackURL,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json',
                   'content-length': str(len(data))}
        try:
            response = requests.post(
                ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']), 'authority': response['Authority']}
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return response
        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}


class OrderVerifyView(LoginRequiredMixin, View):
    def get(request, authority):
        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id=order_id)
        data = {
                "MerchantID": settings.MERCHANT,
                "Amount": order.get_total_price(),
                "Authority": authority,
            }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
        response = requests.post(ZP_API_VERIFY, data=data,headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                order.paid = True
                order.save()
                return {'status': True, 'RefID': response['RefID']}
            else:
                return {'status': False, 'code': str(response['Status'])}
        return response 
    