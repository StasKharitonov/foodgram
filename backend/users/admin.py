from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'is_staff'
    )
    search_fields = (
        'username',
        'email'
    )
    # list_editable = ('role',)
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     ('Дополнительные поля', {'fields': ('bio', 'role')}),
    # )
    # add_fieldsets = BaseUserAdmin.add_fieldsets + (
    #     ('Дополнительные поля', {'fields': ('bio', 'role')}),
    # )
