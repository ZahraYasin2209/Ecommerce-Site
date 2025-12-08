from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)

from .models import (
    ShippingAddress, User
)


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            "recipient_name",
            "recipient_phone_number",
            "recipient_area_postal_code",
            "recipient_address",
            "recipient_email",
        ]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
