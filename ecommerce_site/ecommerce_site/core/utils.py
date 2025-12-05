from django.core.paginator import Paginator

def paginate_queryset(request, queryset, items_per_page=12):
    paginator = Paginator(queryset, items_per_page)
    current_page_number = request.GET.get("page")
    paginated_page = paginator.get_page(current_page_number)

    return paginated_page
