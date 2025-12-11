from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View

from orders.constants import ORDER_SHIPPING_CHARGE
from orders.choices import PaymentStatusChoices
from orders.models import (
    Order, CartItem, Payment, Cart
)
from orders.utils import get_or_create_user_cart
from products.models import ProductDetail
from users.models import ShippingAddress


class OrderReviewView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shipping_address = self.request.user.shipping_address.last()
        cart_items = CartItem.objects.filter(cart__user=self.request.user)

        cart_subtotal = sum(cart_item.quantity * cart_item.product_detail.price
                            for cart_item in cart_items)

        for cart_item in cart_items:
            cart_item.total_price = cart_item.quantity * cart_item.product_detail.price

        context.update({
            "shipping_address": shipping_address,
            "cart_items": cart_items,
            "subtotal": cart_subtotal,
            "shipping_charge": ORDER_SHIPPING_CHARGE,
            "total": cart_subtotal + ORDER_SHIPPING_CHARGE,
        })

        return context


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "orders/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_order = get_object_or_404(
            Order,
            pk=self.kwargs.get("order_pk"),
            user=self.request.user
        )

        context.update({
            "order": user_order,
            "payment": getattr(user_order, "payment", None)
        })

        return context


class ConfirmOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect("orders:checkout")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_cart = get_or_create_user_cart(request.user)

        cart_items = user_cart.cart_items.select_related("product_detail")
        user_shipping_address = request.user.shipping_address.first()

        total_cart_amount = sum(cart_item .quantity * cart_item .product_detail.price
                                for cart_item in cart_items)

        order = Order.objects.create(
            user=request.user,
            shipping_address=user_shipping_address,
            total_amount=total_cart_amount,
        )

        Payment.objects.create(
            amount=total_cart_amount,
            order=order,
            status=PaymentStatusChoices.PENDING
        )

        order_items = [
            order.order_items.model(
                order=order,
                product_detail=cart_item.product_detail,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product_detail.price,
            )
            for cart_item in cart_items
        ]

        order.order_items.bulk_create(order_items)

        product_quantity_updates = {}
        for cart_item in cart_items:
            product_quantity_updates[cart_item.product_detail.pk] = cart_item.quantity

        for product_detail_pk, decrement_quantity in product_quantity_updates.items():
            ProductDetail.objects.filter(pk=product_detail_pk).update(
                stock=F("stock") - decrement_quantity
            )

        cart_items.delete()

        return redirect("orders:success", order_pk=order.pk)
