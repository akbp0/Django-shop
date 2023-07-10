from django.urls import path
from . import views
app_name = "home"
urlpatterns = [
    path("", views.HomeView.as_view(), name='home'),
    path("categories/<slug:slug>/", views.CategoryView.as_view(), name='category'),
    path("categorys/<slug:slug>/", views.HomeView.as_view(), name='cat-slug'),
    path("detail/<slug:slug>/", views.ProductDetailView.as_view(), name="detail")
]
