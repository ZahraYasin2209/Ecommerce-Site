from django.db import models
from django_extensions.db.models import TimeStampedModel
from users.models import User

from .choices import (
    RatingChoices, SizeChoices
)


class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


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
    product_image = models.ImageField(upload_to="product_images/%Y/%m/%d/")
    product_alt_text = models.CharField(max_length=100)

    def __str__(self):
        return f"Image {self.product_image} for {self.product.name}"


class ProductDetail(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="product_details",
    )
    product_size = models.CharField(
        max_length=20,
        choices=SizeChoices.choices,
    )
    product_material = models.CharField(max_length=100)
    product_color = models.CharField(max_length=100)

    product_stock = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()

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
    rating_scale = models.IntegerField(choices=RatingChoices.choices,)
    review_text = models.TextField()

    def __str__(self):
        return f"{self.rating_scale} by {self.user.username} for {self.product.name}"
