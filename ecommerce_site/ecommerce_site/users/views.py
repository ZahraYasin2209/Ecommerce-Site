from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
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
            user.is_superuser = True

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

    success_url = reverse_lazy("account:user_profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["address_form"] = ShippingAddressForm(
            self.request.POST or None,
            instance=self.request.user.shipping_address.last()
        )

        context["last_address"] = self.request.user.shipping_address.last()

        return context

    def form_valid(self, form):
        self.object = form.save()

        address_instance = self.request.user.shipping_address.last()

        address_form = ShippingAddressForm(
            self.request.POST, instance=address_instance
        )

        final_response = super().form_valid(form)

        if address_form.is_valid():
            shipping_address = address_form.save(commit=False)
            shipping_address.user = self.request.user

            if address_instance and address_instance.pk:
                shipping_address.save(
                    update_fields=list(address_form.cleaned_data.keys()) + ["user"]
                )
            else:
                shipping_address.save()

        return final_response


class UserPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, DjangoPasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("account:profile")


class ShippingAddressUpdateView(LoginRequiredMixin, UpdateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "users/address_form.html"

    success_url = reverse_lazy("account:shipping_address")
