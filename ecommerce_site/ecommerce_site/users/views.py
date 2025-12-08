from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

from .forms import (
    CustomLoginForm, CustomUserCreationForm
)


def register_user_view(request):
    form = CustomUserCreationForm(request.POST)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Account created for {user.username}! You are now logged in.")
        redirect_url = reverse('home')
    else:
        redirect_url = None

    context = {
        'form': form
    }
    return redirect(redirect_url) if redirect_url else render(request, 'users/register.html', context)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        requested_next_url = self.request.POST.get("next") or self.request.GET.get("next")
        default_redirect_url = reverse("orders:cart_detail")

        final_redirect_url = (
            default_redirect_url
            if requested_next_url and "/add-to-cart/" in requested_next_url
            else requested_next_url or default_redirect_url
        )

        return final_redirect_url
