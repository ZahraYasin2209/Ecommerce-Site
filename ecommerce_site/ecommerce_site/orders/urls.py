from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path("<int:product_pk>/add_to_cart/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("cart/update/<int:item_pk>/", views.CartItemUpdateView.as_view(), name="cart_item_update"),
    path("cart/remove/<int:item_pk>/", views.CartItemRemoveView.as_view(), name="cart_item_remove"),
    path("success/<int:order_pk>/", views.OrderSuccessView.as_view(), name="success"),
    path("cart/", views.CartDetailView.as_view(), name="cart_detail"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("review/", views.OrderReviewView.as_view(), name="order_review"),
    path("orders/confirm/", views.ConfirmOrderView.as_view(), name="confirm_order"),
]
