from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from .choices import SizeChoices
from .forms import ReviewForm
from .filters import ProductQueryService, ProductFilterSet
from .models import (
    Product, Category, Review
)


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "pk"

    queryset = Product.objects.select_related("category").prefetch_related(
        "product_details", "images", "reviews__user"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        product_details = list(product.product_details.all())

        context.update({
            "details": product_details,
            "default_detail": product_details[0] if product_details else None,
            "images": list(product.images.all()),
            "reviews": product.reviews.all().order_by("-id")[:10],
            "review_form": ReviewForm(),
        })

        return context


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    paginate_by = 12
    context_object_name = "object_list"

    product_query_service = ProductQueryService()

    def get_current_category(self):
        category_id = self.request.GET.get("category_id")

        if not hasattr(self, "current_category"):
            product_category = (
                get_object_or_404(Category, pk=category_id)
                if category_id else None
            )
            self.current_category = product_category

        return self.current_category

    def get_queryset(self):
        queryset = (
            Product.objects.all()
            .select_related("category")
            .prefetch_related("product_details", "images")
        )

        queryset = self.product_query_service.annotate_with_min_price(queryset)

        filter_set = ProductFilterSet(self.request.GET, queryset=queryset)
        product_queryset = filter_set.qs

        product_sort_order = self.request.GET.get("order", "newest")

        product_queryset = self.product_query_service.sort_products(
            product_queryset, product_sort_order
        )

        return product_queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "filter": ProductFilterSet(self.request.GET, queryset=self.get_queryset()),
            "categories": self.product_query_service.get_ordered_categories_with_priority(),
            "current_category": self.get_current_category(),
            "search": self.request.GET.get("search", "").strip(),
            "order": self.request.GET.get("order", "newest"),
            "size": self.request.GET.getlist("size"),
            "size_choices": SizeChoices.choices,
        })

        return context


class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        product = get_object_or_404(
            Product, pk=self.kwargs.get("product_pk")
        )

        form.instance.product = product
        form.instance.user = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "products:product_detail",
            kwargs={"pk": self.kwargs.get("product_pk")}
        )
