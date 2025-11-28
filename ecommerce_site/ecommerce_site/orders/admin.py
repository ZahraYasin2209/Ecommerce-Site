from django.contrib import admin

from .models import (
    Order, OrderItem, Cart, CartItem, Payment
)


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)
