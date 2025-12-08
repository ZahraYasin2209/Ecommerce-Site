from django.contrib import admin

from .models import (
    Category, Product, ProductImage, ProductDetail, Review
)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductDetail)
admin.site.register(Review)
