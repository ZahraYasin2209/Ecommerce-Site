from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)

    category_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=100)
    product_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product_image_id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )

    product_image = models.ImageField(
        "Product Image", upload_to="product_images"
    )

    product_alt_text = models.CharField(max_length=100)

    def __str__(self):
        return f"Image {self.product_image} for {self.product.product_name}"


class ProductDetail(models.Model):
    product_code = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )

    product_size = models.CharField(max_length=100)
    product_material = models.CharField(max_length=100)
    product_color = models.CharField(max_length=100)

    product_stock = models.IntegerField()

    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    product_description = models.TextField()

    def __str__(self):
        return f"{self.product.product_name} Details"


class ReviewAndRating(models.Model):
    review_id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    rating_scale = models.IntegerField(default=1)
    review_text = models.TextField()

    rating_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.rating_scale} by {self.user.username}"
