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

        widgets = {
            "recipient_name": forms.TextInput(attrs={"class": "form-control"}),
            "recipient_phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "recipient_area_postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "recipient_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "recipient_email": forms.EmailInput(attrs={"class": "form-control"}),
        }


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
