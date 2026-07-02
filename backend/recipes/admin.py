from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms.models import BaseInlineFormSet

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        ingredients_count = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue

            ingredient = form.cleaned_data.get('ingredient')
            amount = form.cleaned_data.get('amount')

            if ingredient:
                if not amount or amount < 1:
                    raise ValidationError(
                        'Количество ингредиента должно быть больше 0'
                    )
                ingredients_count += 1

        if ingredients_count < 1:
            raise ValidationError('Добавьте хотя бы один ингредиент')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    formset = RecipeIngredientInlineFormSet
    extra = 1
    min_num = 1
    validate_min = True
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Кол-во добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorited_by'),
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe')
    search_fields = ('id',)
    list_filter = ('id',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
