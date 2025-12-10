from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from orders.models import CartItem
from orders.utils import get_or_create_user_cart
from orders.constants import DEFAULT_CART_ITEMS_PRICE


class CartDetailView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = "orders/cart_detail.html"
    context_object_name = "cart_items"

    def get_queryset(self):
        self.user_cart = get_or_create_user_cart(self.request.user)

        return self.user_cart.cart_items.select_related(
            "product_detail",
            "product_detail__product"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_items = context["cart_items"]
        total_cart_price = DEFAULT_CART_ITEMS_PRICE

        for cart_item in cart_items:
            cart_item.line_total_price = cart_item.quantity * cart_item.product_detail.price
            total_cart_price += cart_item.line_total_price

        context.update({
            "cart": self.user_cart,
            "cart_total": total_cart_price,
        })

        return context
