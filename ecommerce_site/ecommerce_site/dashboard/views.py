from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView, UpdateView,
)

from products.forms import ProductForm, CategoryForm
from products.models import Product, Category
from .mixins import AdminRequiredMixin


class DashboardIndexView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_products"] = Product.objects.count()
        context["total_categories"] = Category.objects.count()

        return context


class ProductListView(AdminRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    queryset = Product.objects.all().order_by("-created")


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_form.html"

    success_url = reverse_lazy("dashboard:product_list")


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_form.html"

    success_url = reverse_lazy("dashboard:product_list")


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product_confirm_delete.html"

    success_url = reverse_lazy("dashboard:product_list")


class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = "dashboard/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_form.html"

    success_url = reverse_lazy("dashboard:category_list")


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_form.html"

    success_url = reverse_lazy("dashboard:category_list")


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = "dashboard/category_confirm_delete.html"

    success_url = reverse_lazy("dashboard:category_list")
