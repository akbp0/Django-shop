from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views import View
from .forms import RegisterForm, VerifyForm, LoginForm
import random
from utils import send_otp_code
from .models import OtpModel, MyUsers
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin


class UserRegisterView(View):
    form_class = RegisterForm
    template_page = "accounts/register_temp.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_page, context={"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(10000, 99999)
            send_otp_code(form.cleaned_data["phone_number"], random_code)
            OtpModel.objects.create(phone_number=form.cleaned_data["phone_number"], code=random_code)
            request.session["user_registeration_info"] = {
                "phone_number": form.cleaned_data["phone_number"],
                "email": form.cleaned_data["email"],
                "full_name": form.cleaned_data["full_name"],
                "password": form.cleaned_data["password1"]
            }
            messages.success(request, "we sent you a 5 digits code", "primary")
            return redirect('accounts:verify')
        return render(request, self.template_page, context={"form": form})


class UserVerifyView(View):
    form_class = VerifyForm
    template_page = "accounts/code.html"

    def get(self, request):
        form = self.form_class
        return render(request, self.template_page, context={"form": form})

    def post(self, request):
        sessions = request.session["user_registeration_info"]
        code_instance = OtpModel.objects.get(phone_number=sessions['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd["code"] == code_instance.code:
                now = datetime.now(code_instance.created.tzinfo)
                if now > code_instance.created + timedelta(minutes=2):
                    messages.error(
                        request,
                        "2 minutes have passed since the verification code was sent.\
                        Please request a new code",
                        "warning"
                        )
                    return render(request, self.template_page, context={"form": form})
                MyUsers.objects.create_user(
                    email=sessions['email'],
                    phone_number=sessions['phone_number'],
                    full_name=sessions['full_name'],
                    password=sessions['password']
                )
                login(request, MyUsers.objects.get(phone_number=sessions['phone_number'], ))
                code_instance.delete()
                messages.success(request, "You have successfully registered", "success")
                return redirect('home:home')
            else:
                messages.error(request, "invalid code", "danger")
                code_instance.delete()
        code_instance.delete()
        return render(request, self.template_page, context={"form": form})


class UserLoginView(View):
    form_class = LoginForm
    temp_page = "accounts/login_temp.html"

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next")
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.temp_page, context={"form": form})

    def post(self, request):
        form = request.POST

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, phone_number=cd['phone_number'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'logged in succesfully', 'success')
                if self.next:
                    return redirect(self.next)
                else:
                    return redirect("home:home")
            else:
                messages.success(request, 'username or password is incorrect', 'warning')
                return render(request, self.temp_page, {"form": form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, ' You logged out from your account', 'danger')
        return redirect("home:home")
