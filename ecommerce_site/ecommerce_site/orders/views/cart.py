from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from orders.models import CartItem
from products.models import Product, ProductDetail
from .utils import get_user_cart


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    product_detail_id = request.POST.get("detail_id") or request.session.pop("add_to_cart_detail", None)
    quantity_to_add = int(request.POST.get("quantity", 1) or request.session.pop("add_to_cart_quantity", 1))

    product_variant = get_object_or_404(
        ProductDetail, id=product_detail_id, product=product
    )
    user_cart = get_user_cart(request.user)

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
    user_cart = get_user_cart(request.user)
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart=user_cart)

    quantity_str = request.POST.get('quantity', str(cart_item.quantity))
    try:
        new_quantity = int(quantity_str)
    except ValueError:
        new_quantity = cart_item.quantity
        messages.error(request, "Invalid quantity value. Using previous quantity.")

    product_name = cart_item.product_detail.product.name

    if new_quantity > 0:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f"Quantity for {product_name} updated to {new_quantity}.")
    else:
        cart_item.delete()
        messages.success(request, f"{product_name} removed from cart.")

    return redirect('orders:cart_detail')


@login_required
@require_POST
def cart_item_remove(request, item_pk):
    cart_item = get_object_or_404(CartItem, pk=item_pk, cart=get_user_cart(request.user))
    product_name = cart_item.product_detail.product.name

    cart_item.delete()
    messages.success(
        request, f"{product_name} was removed from your cart."
    )

    return redirect('orders:cart_detail')
