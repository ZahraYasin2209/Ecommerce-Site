from django.db.models import (
    Q, Min, Case, When, IntegerField
)

from products.models import Product, Category
from .constants import PRODUCT_ORDER_MAPPING


class ProductQueryService:
    def get_base_queryset(self):
        return (
            Product.objects.all()
            .select_related("category")
            .prefetch_related("product_details", "images")
        )

    def filter_by_category(self, product_queryset, category):
        return product_queryset.filter(category=category)

    def apply_search_filter(self, product_queryset, search_query):
        return product_queryset.filter(
            Q(name__icontains=search_query)
            | Q(code__icontains=search_query)
            | Q(product_details__description__icontains=search_query)
            | Q(product_details__material__icontains=search_query)
        ).distinct()

    def filter_by_size(self, product_queryset, size_value):
        if size_value:
            product_queryset = product_queryset.filter(
                product_details__size=size_value
            ).distinct()

        return product_queryset

    def annotate_with_min_price(self, product_queryset):
        return product_queryset.annotate(
            min_price=Min("product_details__price")
        )

    def sort_products(self, product_queryset, product_sort_key):
        product_order_field = PRODUCT_ORDER_MAPPING.get(product_sort_key, "-created")

        return product_queryset.order_by(product_order_field, "name")

    def get_ordered_categories_with_priority(self):
        return Category.objects.annotate(
            order_priority=Case(
                When(name="Others", then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by("order_priority", "name")
