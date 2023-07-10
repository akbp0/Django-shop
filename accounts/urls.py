from django.urls import path
from . import views
app_name = "accounts"
urlpatterns = [
    path("login", views.UserLoginView.as_view(), name='user_Login'),
    path("logout", views.UserLogoutView.as_view(), name='user_logout'),
    path("register", views.UserRegisterView.as_view(), name='user_register'),
    path("verify", views.UserVerifyView.as_view(), name='verify')
]
