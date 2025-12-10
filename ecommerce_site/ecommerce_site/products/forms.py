from django import forms

from products.models import Review, RatingChoices
from .models import (
    Category, ProductDetail, Product
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=RatingChoices.choices, attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "code",
            "category",
        ]


class ProductDetailForm(forms.ModelForm):
    class Meta:
        model = ProductDetail
        fields = [
            "size",
            "material",
            "color",
            "stock",
            "price",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
