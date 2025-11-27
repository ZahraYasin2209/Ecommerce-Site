from django.db import models


class UserRoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    CUSTOMER = "CUSTOMER", "Customer"
