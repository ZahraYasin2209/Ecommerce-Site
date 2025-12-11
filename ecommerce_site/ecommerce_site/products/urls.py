from django.urls import path

from orders.views.add_to_cart import AddToCartView
from .views.product_detail import ProductDetailView
from .views.product_list import ProductListView
from .views.reviews import AddReviewView


app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<int:category_id>/", ProductListView.as_view(), name="category_products"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("<int:product_pk>/add-to-cart/", AddToCartView.as_view(), name='add_to_cart'),
    path("<int:product_pk>/add-review/", AddReviewView.as_view(), name='add_review'),
]
