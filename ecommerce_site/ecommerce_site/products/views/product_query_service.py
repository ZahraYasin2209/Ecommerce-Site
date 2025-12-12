from decimal import Decimal, InvalidOperation
from django.db.models import (
    Q, Min, Case, When, IntegerField
)

from products.constants import (
    DEFAULT_MAX_PRICE,
    DEFAULT_MIN_PRICE,
    PRODUCT_ORDER_MAPPING
)
from products.models import Product, Category


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

    def filter_by_size(self, product_queryset, selected_sizes):
        if selected_sizes:
            product_queryset = product_queryset.filter(
                product_details__size__in=selected_sizes
            ).distinct()

        return product_queryset

    def validate_product_price(
            self, product_price, default_product_price
    ):
        try:
            validated_product_price = Decimal(product_price)
        except (InvalidOperation, TypeError):
            validated_product_price = default_product_price

        return validated_product_price

    def apply_price_filter(self, queryset, min_product_price, max_product_price):
        min_product_price = self.validate_product_price(
            min_product_price,
            DEFAULT_MIN_PRICE,
        )

        max_product_price = self.validate_product_price(
            max_product_price,
            DEFAULT_MAX_PRICE,
        )

        queryset = queryset.filter(
            product_details__price__gte=min_product_price,
            product_details__price__lte=max_product_price,
        )

        return queryset.distinct()

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
