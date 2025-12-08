from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from products.models import Category
from .product_query_service import ProductQueryService


class ProductListView(ListView):
    model = Category
    template_name = "products/product_list.html"

    paginate_by = 12

    context_object_name = "products"
    product_query_service = ProductQueryService()

    def get_current_category(self):
        if not hasattr(self, "current_category"):
            category_id = self.kwargs.get("category_id")
            product_category = (
                get_object_or_404(Category, pk=category_id)
                if category_id else None
            )

            self.current_category = product_category

        return self.current_category

    def get_queryset(self):
        product_queryset = self.product_query_service.get_base_queryset()

        search_query = self.request.GET.get("search", "").strip()
        selected_product_size = self.request.GET.get("size")
        sort_order = self.request.GET.get("order", "newest")

        current_category = self.get_current_category()

        if current_category:
            product_queryset = self.product_query_service.filter_by_category(
                product_queryset, current_category
            )

        product_queryset = self.product_query_service.apply_search_filter(
            product_queryset, search_query
        )

        product_queryset = self.product_query_service.filter_by_size(
            product_queryset, selected_product_size
        )

        product_queryset = self.product_query_service.annotate_with_min_price(product_queryset)

        product_queryset = self.product_query_service.sort_products(
            product_queryset, sort_order
        )

        return product_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "categories": self.product_query_service.get_ordered_categories_with_priority(),
            "current_category": self.get_current_category(),
            "search": self.request.GET.get("search", "").strip(),
            "order": self.request.GET.get("order", "newest"),
            "size": self.request.GET.get("size"),
        })

        return context
