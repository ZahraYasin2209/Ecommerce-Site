from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,
)

from .choices import UserRoleChoices
from .forms import (
    CustomLoginForm,
    CustomUserCreationForm,
    ShippingAddressForm,
    UserProfileUpdateForm,
)
from .models import ShippingAddress, User


class RegisterUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save(commit=False)

        if user.user_role == UserRoleChoices.ADMIN:
            user.is_staff = True

        user.save()
        self.object = user

        login(self.request, user)

        if user.user_role == UserRoleChoices.ADMIN:
            response_redirect = redirect(reverse_lazy("dashboard:index"))
        else:
            response_redirect = redirect(reverse_lazy("home"))

        return response_redirect

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(BaseLoginView):
    authentication_form = CustomLoginForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        needs_save = False

        if user.user_role == UserRoleChoices.ADMIN:
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                needs_save = True

        if needs_save:
            with transaction.atomic():
                user.save(update_fields=["is_staff", "is_superuser"])

        login(self.request, user)

        if user.user_role == UserRoleChoices.ADMIN:
            response_redirect = redirect(reverse_lazy("dashboard:index"))
        else:
            response_redirect = super(BaseLoginView, self).form_valid(form)

        return response_redirect


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm
    template_name = "users/profile_update.html"

    success_url = reverse_lazy("account:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        last_shipping_address = self.request.user.shipping_address.last()

        if self.request.POST:
            context["address_form"] = ShippingAddressForm(
                self.request.POST, instance=last_shipping_address
            )
        else:
            context["address_form"] = ShippingAddressForm(instance=last_shipping_address)

        context["last_address"] = last_shipping_address

        return context

    def form_valid(self, form):
        self.object = form.save()

        address_form = ShippingAddressForm(
            self.request.POST, instance=self.request.user.shipping_address.last()
        )

        if address_form.is_valid():
            shipping_address = address_form.save(commit=False)
            shipping_address.user = self.request.user

            fields_to_save = list(address_form.cleaned_data.keys()) + ["user"]

            shipping_address.save(update_fields=fields_to_save)

        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, DjangoPasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("account:profile")


class ShippingAddressUpdateView(LoginRequiredMixin, UpdateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "users/address_form.html"

    success_url = reverse_lazy("account:shipping_address")

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
