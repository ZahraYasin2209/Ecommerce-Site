from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.urls import (
    reverse, reverse_lazy
)
from django.views.generic.edit import CreateView

from .forms import (
    CustomLoginForm, CustomUserCreationForm
)


class RegisterUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'

    success_url = reverse_lazy('login')

    def form_valid(self, form):
        self.object = user = form.save()
        login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


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
