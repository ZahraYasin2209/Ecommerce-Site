from django.urls import path

from . import views
from .views import CustomLoginView


urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
]
