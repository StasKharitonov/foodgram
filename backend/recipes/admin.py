from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

from recipes.constants import COOKING_TIME_FAST_MAX, COOKING_TIME_MEDIUM_MAX

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        ingredients_count = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            if form.cleaned_data.get('ingredient'):
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


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return (
            (
                'fast',
                f'Быстрые (до {COOKING_TIME_FAST_MAX} мин)',
            ),
            (
                'medium',
                (
                    f'Средние ({COOKING_TIME_FAST_MAX + 1}'
                    f'—{COOKING_TIME_MEDIUM_MAX} мин)'
                ),
            ),
            (
                'long',
                f'Долгие (от {COOKING_TIME_MEDIUM_MAX + 1} мин)',
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lte=COOKING_TIME_FAST_MAX)
        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gt=COOKING_TIME_FAST_MAX,
                cooking_time__lte=COOKING_TIME_MEDIUM_MAX,
            )
        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=COOKING_TIME_MEDIUM_MAX)
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'image_preview',
        'tags_list',
        'ingredients_list',
        'favorites_count',
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags', CookingTimeFilter, 'author')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" width="80" height="60">'
        )

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        return ', '.join(
            recipe_ingredient.ingredient.name
            for recipe_ingredient in obj.recipeingredient_set.all()
        )

    @admin.display(description='Кол-во добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorite'),
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    search_fields = ('ingredient__name', 'recipe__name')
    list_filter = ('ingredient', 'recipe')
    autocomplete_fields = ('ingredient', 'recipe')


class UserRecipeAdminForm(forms.ModelForm):
    duplicate_error_message = 'Такая запись уже существует.'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        recipe = cleaned_data.get('recipe')
        if not user or not recipe:
            return cleaned_data

        duplicates = self._meta.model.objects.filter(
            user=user,
            recipe=recipe,
        )
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError(self.duplicate_error_message)
        return cleaned_data


class FavoriteAdminForm(UserRecipeAdminForm):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartAdminForm(UserRecipeAdminForm):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    form = FavoriteAdminForm
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    form = ShoppingCartAdminForm
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')
