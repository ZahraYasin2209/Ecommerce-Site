import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("orders/", include("orders.urls", namespace="orders")),
    path("products/", include("products.urls", namespace="products")),
    path("users/", include("users.urls", namespace="account")),
    path('admin_dashboard/', include('dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'ecommerce_site/static'))

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
