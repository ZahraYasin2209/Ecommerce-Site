from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import CustomLoginView


app_name = "account"

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileUpdateView.as_view(), name="profile"),
    path("password/change/", views.UserPasswordChangeView.as_view(), name="password_change"),
]
