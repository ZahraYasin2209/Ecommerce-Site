from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from orders.models import CartItem
from products.models import Product, ProductDetail
from orders.utils import get_or_create_user_cart


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    product_detail_id = request.POST.get("detail_id") or request.session.pop("add_to_cart_detail", None)
    quantity_to_add = int(request.POST.get("quantity", 1) or request.session.pop("add_to_cart_quantity", 1))

    product_variant = get_object_or_404(
        ProductDetail, id=product_detail_id, product=product
    )
    user_cart = get_or_create_user_cart(request.user)

    CartItem.objects.create(
        cart=user_cart,
        product=product,
        product_detail=product_variant,
        quantity=quantity_to_add
    )

    return redirect("orders:cart")


@login_required
@require_POST
def update_cart_item_quantity(request, item_pk):
    user_cart = get_or_create_user_cart(request.user)
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart=user_cart)

    cart_item.quantity = int(request.POST.get('quantity', str(cart_item.quantity)))

    cart_item.save(update_fields=["quantity"]) \
        if cart_item.quantity > 0 \
        else cart_item.delete()

    return redirect('orders:cart_detail')


@login_required
@require_POST
def cart_item_remove(request, item_pk):
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart=get_or_create_user_cart(request.user))
    product_name = cart_item.product_detail.product.name

    cart_item.delete()
    messages.success(
        request, f"{product_name} was removed from your cart."
    )

    return redirect('orders:cart_detail')
