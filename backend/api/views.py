from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.constants import MAX_AUTHOR_RECIPES
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import PageNumberPagination
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, SetAvatarSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserWithRecipesSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipeingredient_set__ingredient'
    )
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in (
            'create', 'download_shopping_cart',
            'favorite', 'shopping_cart'
        ):
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), AuthorOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(AllowAny,)
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(
            f'/api/recipes/{recipe.id}/'
        )
        return Response({'short-link': url})

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        cart_items = request.user.shopping_cart_items.all()
        if not cart_items:
            return Response(
                {'errors': ['Список покупок пуст']},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = {}
        for cart_item in cart_items:
            for ri in cart_item.recipe.recipeingredient_set.all():
                name = ri.ingredient.name
                if name in ingredients:
                    ingredients[name]['amount'] += ri.amount
                else:
                    ingredients[name] = {
                        'amount': ri.amount,
                        'unit': ri.ingredient.measurement_unit
                    }
        lines = [
            f'{name} ({data["unit"]}) — {data["amount"]}'
            for name, data in sorted(ingredients.items())
        ]
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not favorite:
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': ['Рецепт уже в списке покупок']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not cart_item:
            return Response(
                {'errors': ['Рецепта нет в списке покупок']},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class UserViewSet(DjoserUserViewSet):
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in (
            'me', 'avatar', 'subscriptions', 'subscribe',
            'set_password', 'destroy'
        ):
            return (IsAuthenticated(),)
        if self.action == 'list':
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return UserWithRecipesSerializer
        if self.action == 'subscribe':
            return UserWithRecipesSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        recipes_limit = self._get_recipes_limit(request)
        subscribed_to_ids = Subscription.objects.filter(
            subscriber=request.user
        ).values_list('subscribed_to_id', flat=True)
        authors = User.objects.filter(
            id__in=subscribed_to_ids
        ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(authors)
        context = {
            'request': request,
            'recipes_limit': recipes_limit,
        }
        serializer = UserWithRecipesSerializer(
            page if page is not None else authors,
            many=True,
            context=context
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        try:
            author_id = int(id)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                subscriber=request.user, subscribed_to=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                subscriber=request.user, subscribed_to=author
            )
            author = User.objects.filter(id=author_id).annotate(
                recipes_count=Count('recipes')
            ).first()
            recipes_limit = self._get_recipes_limit(request)
            serializer = UserWithRecipesSerializer(
                author,
                context={
                    'request': request,
                    'recipes_limit': recipes_limit,
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(
            subscriber=request.user, subscribed_to=author
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar_url})
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _get_recipes_limit(request):
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            return int(recipes_limit)
        return MAX_AUTHOR_RECIPES
