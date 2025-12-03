from django.views.generic import DetailView

from products.models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return (
            Product.objects.select_related("category")
            .prefetch_related("product_details", "images", "reviews__user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        product_detail_items = list(product.product_details.all())
        context["details"] = product_detail_items
        context["default_detail"] = product_detail_items[0] if product_detail_items else None

        context["images"] = list(product.images.all())
        context["reviews"] = product.reviews.all().order_by("-id")[:10]

        return context
