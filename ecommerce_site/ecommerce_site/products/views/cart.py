from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from orders.models import Cart, CartItem
from orders.utils import get_or_create_user_cart
from products.models import ProductDetail


@login_required(login_url='login')
@require_POST
def add_to_cart(request, product_pk):
    product_detail_id = request.POST.get("detail_id")

    try:
        quantity_to_add = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity_to_add = 0

    product_detail = get_object_or_404(ProductDetail, pk=product_detail_id)

    cart_item, is_created = CartItem.objects.get_or_create(
        cart=get_or_create_user_cart(request.user),
        product_detail=product_detail,
        defaults={"quantity": quantity_to_add}
    )

    if not is_created:
        cart_item.quantity += quantity_to_add
        cart_item.save(update_fields=["quantity"])
    else:
        pass

    return redirect(reverse("orders:cart_detail"))


@login_required(login_url='login')
def display_cart_contents(request):
    user_cart = get_or_create_user_cart(request.user)

    cart_items = user_cart.cart_items.select_related(
        "product_detail",
        "product_detail__product"
    )

    total_cart_price = 0
    for cart_item in cart_items:
        cart_item.line_total_price = cart_item.quantity * cart_item.product_detail.price
        total_cart_price += cart_item.line_total_price

    context = {
        "cart": user_cart,
        "cart_items": cart_items,
        "cart_total": total_cart_price,
    }

    return render(request, "orders/cart_detail.html", context)
