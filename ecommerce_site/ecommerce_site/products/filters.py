import django_filters
from django.db.models import (
    Q, Min, Case, When, IntegerField
)

from .choices import SizeChoices
from .constants import PRODUCT_ORDER_MAPPING
from .models import (
    Product, Category
)


class ProductFilterSet(django_filters.FilterSet):
    category_id = django_filters.NumberFilter(
        field_name="category__pk",
        lookup_expr="exact",
        label="Category ID"
    )

    product_min_price = django_filters.NumberFilter(
        field_name="product_details__price",
        lookup_expr="gte",
        label="Product Minimum Price"
    )

    product_max_price = django_filters.NumberFilter(
        field_name="product_details__price",
        lookup_expr="lte",
        label="Product Maximum Price"
    )

    selected_product_size = django_filters.MultipleChoiceFilter(
        field_name="product_details__size",
        lookup_expr="in",
        choices=SizeChoices.choices,
        label="Size"
    )

    search_query = django_filters.CharFilter(method="filter_search", label="Search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(code__icontains=value)
            | Q(product_details__description__icontains=value)
            | Q(product_details__material__icontains=value)
        ).distinct()


    class Meta:
        model = Product
        fields = [
            "category_id", "product_min_price", "product_max_price", "selected_product_size", "search_query"
        ]


class ProductQueryService:
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
