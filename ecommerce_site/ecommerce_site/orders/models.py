from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    total_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    shipping_address_id = models.ForeignKey(
        'ShippingAddress', on_delete=models.CASCADE
    )

    order_created_at = models.DateTimeField(auto_now_add=True)
    order_status = models.BooleanField(default=False)

    order_status_choices = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Order {self.total_order_amount} by {self.user.username}"


class OrderItem(models.Model):
    item_id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE
    )

    item_quantity = models.IntegerField(default=1)

    item_price_at_purchase = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    def __str__(self):
        return f"{self.product.product_name} in Order {self.order.order_id}"


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )

    cart_created_at = models.DateTimeField(auto_now_add=True)

    cart_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username} by {self.cart_created_at}"


class CartItem(models.Model):
    item_id = models.AutoField(primary_key=True)

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE
    )

    product_quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.product_name} with quantity {self.product_quantity}"


class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    )

    payment_id = models.AutoField(primary_key=True)

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE
    )

    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_amount} for Order {self.order.order_id}"
