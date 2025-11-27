from django.db import models
from django_extensions.db.models import TimeStampedModel

from .choices import (
    RatingChoices, SizeChoices
)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "products.Category",
        on_delete=models.CASCADE,
        related_name="product",
    )

    def __str__(self):
        return self.name


class ProductImage(TimeStampedModel):
    image = models.ImageField(upload_to="product_images/%Y/%m/%d/")
    alt_text = models.CharField(max_length=100)

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )

    def __str__(self):
        return f"Image {self.image} for {self.product.name}"


class ProductDetail(models.Model):
    size = models.CharField(max_length=20, choices=SizeChoices.choices)
    material = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="product_details",
    )

    def __str__(self):
        return f"{self.product.name} Details"


class Review(models.Model):
    rating = models.IntegerField(choices=RatingChoices.choices,)
    comment = models.TextField()

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="review",
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="review",
    )

    def __str__(self):
        return f"{self.rating} by {self.user.username} for {self.product.name}"
