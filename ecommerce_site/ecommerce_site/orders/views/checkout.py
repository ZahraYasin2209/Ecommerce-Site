from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from users.forms import ShippingAddressForm
from users.models import ShippingAddress


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
