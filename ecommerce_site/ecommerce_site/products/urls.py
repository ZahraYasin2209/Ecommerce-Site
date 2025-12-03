from django.urls import path

from .views.product_list import ProductListView
from .views.product_detail import ProductDetailView
from .views.cart import add_to_cart


app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("category/<int:category_id>/", ProductListView.as_view(), name="category_products"),
    path("<int:pk>/", ProductDetailView.as_view(), name="detail"),
    path("<int:product_pk>/add-to-cart/", add_to_cart, name="add_to_cart"),
]
