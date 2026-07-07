from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'recipes_count',
        'subscribers_count',
        'is_staff',
    )
    search_fields = (
        'email',
        'username',
    )
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {
            'fields': ('username', 'first_name', 'last_name', 'avatar')
        }),
        ('Права доступа', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            )
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2',
            ),
        }),
    )

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes_count

    @admin.display(description='Подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes'),
            subscribers_count=Count('author_subscriptions'),
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = (
        'user__email',
        'user__username',
        'author__email',
        'author__username',
    )
    list_filter = ('user', 'author')
    autocomplete_fields = ('user', 'author')
