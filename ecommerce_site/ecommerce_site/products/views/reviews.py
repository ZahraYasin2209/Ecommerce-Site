from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from products.forms import ReviewForm
from products.models import Product, Review


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_review_form = ReviewForm(request.POST)
        if product_review_form.is_valid():
            Review.objects.create(
                product=product,
                user=request.user,
                rating=product_review_form.cleaned_data['rating'],
                comment=product_review_form.cleaned_data['comment']
            )

    return redirect('products:detail', pk=product.id)
