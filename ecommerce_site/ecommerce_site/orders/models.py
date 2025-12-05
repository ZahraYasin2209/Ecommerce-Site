from django.core.validators import MinValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .choices import (
    OrderStatusChoices, PaymentStatusChoices
)


class Order(TimeStampedModel):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING,
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )

    shipping_address = models.ForeignKey(
        "users.ShippingAddress",
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Order {self.total_amount} by {self.user.username}"


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="order_items"
    )

    product_detail = models.ForeignKey(
        "products.ProductDetail",
        on_delete=models.CASCADE,
        related_name="order_items",
    )

    def __str__(self):
        return f"{self.product_detail.product_name} in Order {self.order.id}"


class Cart(TimeStampedModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    product_detail = models.ForeignKey(
        "products.ProductDetail",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    cart = models.ForeignKey(
        "orders.Cart",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    def __str__(self):
        return f"{self.product_detail.product.name} with quantity {self.quantity}"


class Payment(TimeStampedModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment {self.amount} for Order {self.order.id}"
