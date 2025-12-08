import os

from django.contrib import admin
from django.urls import path, include

from .views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("products/", include("products.urls", namespace="products")),
    path("users/", include("users.urls")),
]
