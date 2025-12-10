from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ShippingAddress


class CustomUserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ("user_role",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('user_role',)}),
    )

    def has_view_permission(self, request, obj=None):
        permission_granted = super().has_view_permission(request, obj)
        if request.user.is_superuser:
            permission_granted = True

        return permission_granted

    def has_change_permission(self, request, obj=None):
        permission_changed = super().has_change_permission(request, obj)
        if request.user.is_superuser:
            permission_changed = True

        return permission_changed

    def has_add_permission(self, request):
        add_permissions = super().has_add_permission(request)
        if request.user.is_superuser:
            add_permissions = True

        return add_permissions

    def has_delete_permission(self, request, obj=None):
        delete_permissions = super().has_delete_permission(request, obj)
        if request.user.is_superuser:
            delete_permissions = True

        return delete_permissions

    def has_module_permission(self, request):
        module_permissions = super().has_module_permission(request)
        if request.user.is_superuser:
            module_permissions = True

        return module_permissions

    def has_change_permission(self, request, obj=None):
        change_permissions = super().has_change_permission(request, obj)
        if request.user.is_superuser:
            change_permissions = True

        return change_permissions

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
