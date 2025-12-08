from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from users.forms import ShippingAddressForm


@login_required(login_url='login')
def checkout(request):
    saved_address = request.user.shipping_address.last()
    shipping_address_form = ShippingAddressForm(request.POST or None, instance=saved_address)

    redirect_response = None

    if request.method == "POST" and shipping_address_form.is_valid():
        shipping_address = shipping_address_form.save(commit=False)
        shipping_address.user = request.user

        if saved_address:
            shipping_address.save(update_fields=shipping_address_form.changed_data)
        else:
            shipping_address.save()

        redirect_response = redirect("orders:order_review")

    return redirect_response or render(
        request,
        "orders/checkout.html",
        {"form": shipping_address_form, "saved_address": saved_address}
    )
