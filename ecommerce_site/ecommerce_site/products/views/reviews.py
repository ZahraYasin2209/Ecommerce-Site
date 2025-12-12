from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, reverse
from django.views.generic.edit import CreateView

from products.forms import ReviewForm
from products.models import Product, Review


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
            "products:detail",
            kwargs={"pk": self.kwargs.get("product_pk")}
        )
