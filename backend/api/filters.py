import django_filters
from django_filters import FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    author = django_filters.NumberFilter(method='filter_author')
    tags = django_filters.Filter(method='filter_tags')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        tag_slugs = self.request.query_params.getlist('tags')
        tag_slugs = [
            slug.strip() for slug in tag_slugs if slug and slug.strip()
        ]
        if not tag_slugs:
            return queryset
        return queryset.filter(tags__slug__in=tag_slugs).distinct()

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
