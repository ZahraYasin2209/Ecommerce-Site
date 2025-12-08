from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404, redirect
)
from django.views import View

from orders.models import CartItem
from orders.utils import get_or_create_user_cart


class CartItemUpdateView(LoginRequiredMixin, View):
    def post(self, request, item_pk):
        user_cart = get_or_create_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, pk=item_pk, cart=user_cart)

        cart_item.quantity = int(request.POST.get("quantity", str(cart_item.quantity)))

        if cart_item.quantity > 0:
            cart_item.save(update_fields=["quantity"])
        else:
            cart_item.delete()

        return redirect("orders:cart_detail")
