from django.db import models


class OrderStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    CANCELED = "CANCELED", "Canceled"


class PaymentStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    DONE = "DONE", "Done"
    FAILED = "FAILED", "Failed"
    
