from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='category/%y/%m/%d', blank=True, null=True)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name

    def get_absloute_url(self):
        return reverse("home:cat-slug", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='product/%y/%m/%d')
    description = models.TextField()
    price = models.IntegerField()
    avalibale = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name

    def get_absloute_url(self):
        return reverse("home:detail", args=[self.slug])
