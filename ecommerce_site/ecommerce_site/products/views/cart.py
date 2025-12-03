from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from orders.models import Cart, CartItem
from products.models import Product


@login_required
def add_to_cart(request, product_pk):

    redirect_url = request.META.get("HTTP_REFERER", reverse("products:list"))

    if request.method == "POST":
        product_variant_id = request.POST.get("detail_id")
        quantity_to_add = int(request.POST.get("quantity", 1))

        product_variant = get_object_or_404(Product.product_details.through, pk=product_variant_id)

        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product_detail=product_variant,
            defaults={"quantity": quantity_to_add}
        )

        if not created:
            cart_item.quantity += quantity_to_add
            cart_item.save()

        redirect_url = reverse("cart:detail")

    return redirect(redirect_url)
