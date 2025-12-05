from django.views.generic import DetailView

from products.models import Product
from products.forms import ReviewForm
from products.choices import SizeChoices


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
