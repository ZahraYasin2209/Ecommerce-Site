from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    CartItemRemoveView,
    CartItemUpdateView,
    CheckoutView,
    ConfirmOrderView,
    OrderReviewView,
    OrderSuccessView,
)


app_name = "orders"

urlpatterns = [
    path("<int:product_pk>/add_to_cart/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/update/<int:item_pk>/", CartItemUpdateView.as_view(), name="cart_item_update"),
    path("cart/remove/<int:item_pk>/", CartItemRemoveView.as_view(), name="cart_item_remove"),
    path("cart/", CartDetailView.as_view(), name="cart_detail"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("review/", OrderReviewView.as_view(), name="order_review"),
    path("order/confirm/", ConfirmOrderView.as_view(), name="confirm_order"),
    path("success/<int:order_pk>/", OrderSuccessView.as_view(), name="order_success"),
]
