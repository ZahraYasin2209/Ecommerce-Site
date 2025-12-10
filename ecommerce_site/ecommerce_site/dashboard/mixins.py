from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

from users.choices import UserRoleChoices


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        User = get_user_model()
        authorization_response = None

        if not request.user.is_authenticated:
            authorization_response = redirect(reverse_lazy("account:login") + "?next=" + request.path)

        if authorization_response is None:
            try:
                active_user = User.objects.get(pk=request.user.pk)
            except User.DoesNotExist:
                authorization_response = redirect(reverse_lazy("account:login"))

            else:
                if active_user.user_role != UserRoleChoices.ADMIN:
                    authorization_response = redirect(reverse_lazy("home"))
                else:
                    request.user = active_user
                    authorization_response = super().dispatch(request, *args, **kwargs)

        return authorization_response
