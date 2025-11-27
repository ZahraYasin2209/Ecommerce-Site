from django.core.validators import MinValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from users.models import User

from .choices import (
    OrderStatusChoices, PaymentStatusChoices
)


class Order(TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey(
        "users.ShippingAddress",
        on_delete=models.CASCADE,
        related_name="shipping_address",
    )
    order_status = models.CharField(
        max_length=10,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING,
    )

    def __str__(self):
        return f"Order {self.total_order_amount} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    item_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    item_price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} in Order {self.order.id}"


class Cart(TimeStampedModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        "orders.Cart",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.product_name} with quantity {self.quantity}"


class Payment(TimeStampedModel):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )

    def __str__(self):
        return f"Payment {self.payment_amount} for Order {self.order.id}"
