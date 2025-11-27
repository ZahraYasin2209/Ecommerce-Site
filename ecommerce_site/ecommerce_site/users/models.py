from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .choices import UserRoleChoices


class User(TimeStampedModel, AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    user_role = models.CharField(
        max_length=10,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.ADMIN,
    )

    def __str__(self):
        return self.username


class ShippingAddress(TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_shipping_address"
    )

    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField(max_length=100)
    recipient_phone = models.CharField(max_length=20)
    recipient_address = models.TextField()
    recipient_area_postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Address {self.recipient_address} for {self.user.username}"
