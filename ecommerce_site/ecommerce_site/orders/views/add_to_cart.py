from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404, redirect
)
from django.urls import reverse
from django.views import View

from orders.models import CartItem
from orders.utils import get_or_create_user_cart
from products.models import ProductDetail


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_pk):
        quantity_to_add = int(request.POST.get("quantity", 1))

        product_detail = get_object_or_404(
            ProductDetail,
            pk=request.POST.get("detail_id")
        )
        user_cart = get_or_create_user_cart(request.user)

        cart_item, is_created = CartItem.objects.get_or_create(
            cart=user_cart,
            product_detail=product_detail,
            defaults={"quantity": quantity_to_add}
        )

        if not is_created:
            cart_item.quantity += quantity_to_add
            cart_item.save(update_fields=["quantity"])

        return redirect(reverse("orders:cart_detail"))
