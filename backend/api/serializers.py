from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import (MAX_COOKING_TIME, MIN_COOKING_TIME,
                               MIN_INGREDIENT_AMOUNT)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriptions.filter(author=obj).exists()
        )

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeImageMixin:
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(RecipeImageMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        error_messages={
            'min_value': (
                f'Количество ингредиента должно быть '
                f'не менее {MIN_INGREDIENT_AMOUNT}'
            ),
        },
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        error_messages={
            'min_value': (
                f'Время приготовления должно быть '
                f'не менее {MIN_COOKING_TIME} минуты'
            ),
            'max_value': (
                f'Время приготовления не должно превышать '
                f'{MAX_COOKING_TIME} минут'
            ),
        },
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'cooking_time',
            'tags', 'ingredients'
        )

    def validate_image(self, value):
        if self.instance is None and not value:
            raise serializers.ValidationError('Изображение обязательно')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )
        ingredient_ids = [item['ingredient'].pk for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Нужен хотя бы 1 тег')
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться')
        return value

    @staticmethod
    def _create_ingredients(recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount'],
            )
            for item in ingredients_data
        )

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags_data)
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        super().update(instance, validated_data)
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self._create_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(RecipeImageMixin, serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')

    def validate(self, attrs):
        model = self.Meta.model
        if model.objects.filter(
            user=attrs['user'],
            recipe=attrs['recipe'],
        ).exists():
            raise serializers.ValidationError(
                {
                    'errors': (
                        f'Рецепт уже в {model._meta.verbose_name}'
                    ),
                }
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context,
        ).data


class FavoriteSerializer(UserRecipeSerializer):
    class Meta(UserRecipeSerializer.Meta):
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(UserRecipeSerializer):
    class Meta(UserRecipeSerializer.Meta):
        model = ShoppingCart
        fields = ('user', 'recipe')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, attrs):
        if attrs['user'] == attrs['author']:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя'}
            )
        if Subscription.objects.filter(
            user=attrs['user'],
            author=attrs['author'],
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого автора'}
            )
        return attrs

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.author,
            context=self.context,
        ).data


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            limit_param = request.query_params.get('recipes_limit')
            if limit_param:
                try:
                    recipes_limit = int(limit_param)
                except (TypeError, ValueError):
                    recipes_limit = None
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
