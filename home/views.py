from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Category, Product
from orders.forms import CartAddForm


class HomeView(View):
    def get(self, request, slug=None):
        category = None
        products = Product.objects.filter(avalibale=True)
        categories = Category.objects.all()
        if slug:
            category = Category.objects.get(slug=slug)
            products = products.filter(category=category)
        return render(request, "index.html", {"products": products, "categories": categories, "category": category})


class CategoryView(View, ):
    def get(self, request, slug):
        products = Product.objects.filter(avalibale=True)
        category = Category.objects.get(slug=slug)
        products = products.filter(category=category)
        return render(request, "catgory.html", {"products": products, "category": category})


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = CartAddForm()
        return render(request, "product.html", {"product": product, "form": form})
