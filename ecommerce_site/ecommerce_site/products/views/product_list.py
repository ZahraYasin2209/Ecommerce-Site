from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.views import View

from products.models import Category
from .product_query_service import ProductQueryService


class ProductListView(View):
    products_per_page = 12
    product_service = ProductQueryService()

    def get(self, request, category_id=None):
        product_queryset = self.product_service.get_base_queryset()

        current_category = None
        if category_id:
            current_category = get_object_or_404(Category, pk=category_id)
            product_queryset = self.product_service.filter_by_category(
                product_queryset, current_category
            )

        search_query = request.GET.get("search", "").strip()
        product_queryset = self.product_service.apply_search_filter(
            product_queryset,
            search_query
        )

        selected_size = request.GET.get("size")
        product_queryset = self.product_service.filter_by_size(
            product_queryset, selected_size
        )

        product_queryset = self.product_service.annotate_with_min_price(product_queryset)

        sort_order = request.GET.get("order", "newest")
        product_queryset = self.product_service.sort_products(
            product_queryset, sort_order
        )

        products_paginator = Paginator(product_queryset, self.products_per_page)
        current_page = products_paginator.get_page(request.GET.get("page", 1))

        context = {
            "object_list": current_page.object_list,
            "page_obj": current_page,
            "paginator": products_paginator,
            "categories": self.product_service.get_ordered_categories_with_priority(),
            "current_category": current_category,
            "search": search_query,
            "order": sort_order,
            "size": selected_size,
        }

        return render(request, "products/product_list.html", context)
