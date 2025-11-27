from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model

from .choices import (
    RatingChoices, SizeChoices
)

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(
        "products.Category",
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="product_images/%Y/%m/%d/")
    alt_text = models.CharField(max_length=100)

    def __str__(self):
        return f"Image {self.image} for {self.product.name}"


class ProductDetail(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="product_details",
    )

    size = models.CharField(max_length=20,choices=SizeChoices.choices)
    material = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.product.name} Details"


class ReviewAndRating(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="product_rating",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_reviews",
    )

    rating_scale = models.IntegerField(choices=RatingChoices.choices)
    review_text = models.TextField()

    def __str__(self):
        return f"{self.rating_scale} by {self.user.username} for {self.product.name}"
