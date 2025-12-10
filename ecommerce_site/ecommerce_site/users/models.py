from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .choices import UserRoleChoices


class User(TimeStampedModel, AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )

    user_role = models.CharField(
        max_length=15,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.CUSTOMER,
    )

    def __str__(self):
        return self.username


class ShippingAddress(TimeStampedModel):
    recipient_name = models.CharField(max_length=100)
    recipient_phone_number = models.CharField(
        max_length=20,
        help_text="Enter phone number with country code, e.g: +92-345-2345678"
    )

    recipient_area_postal_code = models.CharField(max_length=20)
    recipient_address = models.TextField()
    recipient_email = models.EmailField(max_length=100)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="shipping_address"
    )

    def __str__(self):
        return f"Address {self.recipient_address} for {self.user.username}"
