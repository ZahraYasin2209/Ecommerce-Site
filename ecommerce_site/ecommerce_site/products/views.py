from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Min, Q, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from .models import Product, Category
from orders.models import Cart, CartItem


PRODUCT_ORDER_MAPPING = {
    'price_asc': 'min_price',
    'price_desc': '-min_price',
    'newest': '-created'
}


class ProductListView(View):
    paginate_by = 12

    def get(self, request, category_id=None):
        search_query = request.GET.get('q', '').strip()
        selected_size = request.GET.get('size')
        sort_order = request.GET.get('order', 'newest')

        products = (
            Product.objects.all()
            .select_related('category')
            .prefetch_related('product_details', 'images')
        )

        current_category = None
        if category_id:
            current_category = get_object_or_404(Category, pk=category_id)
            products = products.filter(category=current_category)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(code__icontains=search_query)
                | Q(product_details__description__icontains=search_query)
                | Q(product_details__material__icontains=search_query)
            ).distinct()

        if selected_size:
            products = products.filter(product_details__size=selected_size).distinct()

        products = products.annotate(min_price=Min('product_details__price'))

        order_by_field = PRODUCT_ORDER_MAPPING.get(sort_order, '-created')
        products = products.order_by(order_by_field, 'name')

        paginator = Paginator(products, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        categories = Category.objects.annotate(
            order_priority=Case(
                When(name='Others', then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('order_priority', 'name')

        context = {
            'object_list': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'categories': categories,
            'current_category': current_category,
            'q': search_query,
            'order': sort_order,
            'size': selected_size,
        }

        return render(request, 'products/product_list.html', context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return (
            Product.objects.select_related('category')
            .prefetch_related('product_details', 'images', 'reviews__user')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        details = list(product.product_details.all())
        context['details'] = details
        context['default_detail'] = details[0] if details else None

        context['images'] = list(product.images.all())

        context['reviews'] = product.reviews.all().order_by('-id')[:10]

        return context


@login_required
def add_to_cart(request, product_pk):
    """
    Adds a product variant to the user's cart.
    Expects POST: detail_id (ProductDetail pk), quantity (int)
    """
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', reverse('products:list')))

    variant_id = request.POST.get('detail_id')
    quantity = int(request.POST.get('quantity', 1))

    product_detail = get_object_or_404(
        Product.product_details.through, pk=variant_id
    )

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product_detail=product_detail,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart:detail')
