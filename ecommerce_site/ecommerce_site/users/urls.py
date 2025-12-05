from django.urls import path

from . import views
from .views import CustomLoginView


urlpatterns = [
    path('register/', views.register_user_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
]
