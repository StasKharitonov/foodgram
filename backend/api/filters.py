import django_filters
from django_filters import FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class RecipeFilter(FilterSet):
    author = django_filters.NumberFilter(method='filter_author')
    tags = CharInFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_author(self, queryset, name, value):
        if value is None:
            return queryset
        try:
            return queryset.filter(author_id=int(value))
        except (ValueError, TypeError):
            return queryset.none()

    def filter_is_favorited(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.data.getlist('tags'):
            queryset = queryset.distinct()
        return queryset
