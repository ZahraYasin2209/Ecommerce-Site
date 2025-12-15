from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    TemplateView,
    UpdateView,
)

from products.models import ProductDetail
from users.forms import ShippingAddressForm
from users.models import ShippingAddress
from .choices import PaymentStatusChoices
from .constants import (
    DEFAULT_CART_ITEMS_PRICE,
    ORDER_SHIPPING_CHARGE
)
from .models import (
    CartItem,
    Order,
    Payment
)
from .utils import get_or_create_user_cart


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


class CheckoutView(LoginRequiredMixin, UpdateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "orders/checkout.html"

    success_url = reverse_lazy("orders:order_review")

    def get_object(self, queryset=None):
        return self.request.user.shipping_address.last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["saved_address"] = self.object

        return context

    def form_valid(self, form):
        shipping_address = form.save(commit=False)
        shipping_address.user = self.request.user

        is_creating_new = self.object is None

        if is_creating_new:
            shipping_address.save()
            self.object = shipping_address
        else:
            shipping_address.save(update_fields=form.changed_data)

        return redirect(self.get_success_url())


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
        return redirect('orders:checkout')

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

        return redirect("orders:order_success", order_pk=order.pk)


class CartItemRemoveView(LoginRequiredMixin, View):
    def post(self, request, item_pk):
        cart_item = get_object_or_404(
            CartItem,
            pk=item_pk,
            cart=get_or_create_user_cart(request.user)
        )

        cart_item.delete()

        return redirect("orders:cart_detail")


class CartItemUpdateView(LoginRequiredMixin, View):
    def post(self, request, item_pk):
        user_cart = get_or_create_user_cart(request.user)
        cart_item = get_object_or_404(CartItem, pk=item_pk, cart=user_cart)

        cart_item.quantity = int(request.POST.get("quantity", str(cart_item.quantity)))

        cart_item.save(update_fields=["quantity"]) \
            if cart_item.quantity > 0 \
            else cart_item.delete()

        return redirect("orders:cart_detail")
