from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)

    email = models.EmailField(
        max_length=254, unique=True
    )

    date_joined = models.DateTimeField(default=timezone.now)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )

    user_role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='admin'
    )

    def __str__(self):
        return self.username


class ShippingAddress(models.Model):
    shipping_address_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField(max_length=100)
    recipient_phone = models.CharField(max_length=20)

    recipient_address = models.TextField()
    recipient_area_postal_code = models.IntegerField(default=0)

    def __str__(self):
        return f"Address {self.recipient_address} for {self.user.username}"
