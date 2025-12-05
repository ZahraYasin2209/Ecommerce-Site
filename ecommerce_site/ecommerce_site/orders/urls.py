from django.urls import path

from products.views.cart import display_cart_contents
from . import views
from .views import (
    checkout, order_review
)


app_name = "orders"

urlpatterns = [
    path('<int:product_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path("cart/", display_cart_contents, name="cart_detail"),
    path('cart/update/<int:item_pk>/', views.update_cart_item_quantity, name='cart_item_update'),
    path('cart/remove/<int:item_pk>/', views.cart_item_remove, name='cart_item_remove'),
    path('order-success/<int:order_pk>/', views.order_success, name='order_success'),
    path("checkout/", checkout, name="checkout"),
    path('review/', order_review, name='order_review'),
    path('confirm/', views.confirm_order, name='confirm_order'),
    path('success/<int:order_pk>/', views.order_success, name='success'),
]
