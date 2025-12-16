from django.urls import path

from orders.views import AddToCartView
from .views import (
    ProductDetailView,
    ProductListView,
    AddReviewView
)


app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("<int:product_pk>/add-item/", AddToCartView.as_view(), name='add_to_cart'),
    path("<int:product_pk>/add-review/", AddReviewView.as_view(), name='add_review'),
]
