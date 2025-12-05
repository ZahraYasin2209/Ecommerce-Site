from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from orders.choices import PaymentStatusChoices
from orders.models import (
    Order, CartItem, Payment
)
from users.models import ShippingAddress
from .utils import get_user_cart


@login_required
def order_review(request):
    shipping_address = ShippingAddress.objects.filter(user=request.user).last()
    cart_items = CartItem.objects.filter(cart__user=request.user)

    cart_subtotal = sum(item.quantity * item.product_detail.price
                        for item in cart_items)
    shipping_charge = 10
    order_total_amount = cart_subtotal + shipping_charge

    for cart_item in cart_items:
        cart_item.total_price = cart_item.quantity * cart_item.product_detail.price

    context = {
        'shipping_address': shipping_address,
        'cart_items': cart_items,
        'subtotal': cart_subtotal,
        'shipping_charge': shipping_charge,
        'total': order_total_amount ,
    }

    return render(request, 'orders/order_review.html', context)


@login_required
def order_success(request, order_pk):
    user_order = get_object_or_404(Order, pk=order_pk, user=request.user)
    order_payment = getattr(user_order, 'payment', None)

    return render(
        request, 'orders/success.html',
        {'order': user_order, 'payment': order_payment}
    )


@login_required
def confirm_order(request):
    redirect_url = redirect('orders:checkout')

    if request.method == 'POST':
        user_cart = get_user_cart(request.user)
        cart_items = user_cart.cart_items.all()

        if cart_items.exists():
            user_shipping_address = request.user.shipping_address.first()

            if user_shipping_address:
                total_cart_amount = sum(item.quantity * item.product_detail.price
                                        for item in cart_items)

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

                for cart_item in cart_items:
                    order.order_items.create(
                        product_detail=cart_item.product_detail,
                        quantity=cart_item.quantity,
                        price_at_purchase=cart_item.product_detail.price,
                    )
                cart_items.delete()

                redirect_url = redirect('orders:success', order_pk=order.pk)

    return redirect_url
