from djoser.serializers import (TokenCreateSerializer, UserCreateSerializer,
                                UserSerializer)
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from recipes.constants import MAX_AUTHOR_RECIPES, MAX_LEN_NAME
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Subscription,
                            Tag)
from users.models import User

from .fields import Base64ImageField


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password'].required = True

    def validate(self, attrs):
        try:
            self.user = User.objects.get(email=attrs.get('email'))
        except User.DoesNotExist:
            self.fail('invalid_credentials')
        if not self.user.check_password(attrs.get('password')):
            self.fail('invalid_credentials')
        if not self.user.is_active:
            self.fail('invalid_credentials')
        return attrs

    def create(self, validated_data):
        token, created = Token.objects.get_or_create(user=self.user)
        return {'auth_token': token.key}


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj == request.user:
                return False
            return Subscription.objects.filter(
                subscriber=request.user,
                subscribed_to=obj
            ).exists()
        return False

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


class RecipeSerializer(RecipeImageMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.in_shopping_cart.filter(user=request.user).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'cooking_time',
            'tags', 'ingredients'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )
        ingredient_ids = []
        for item in value:
            ingredient_id = item.get('id')
            amount = item.get('amount')
            try:
                amount = int(amount)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    'Количество должно быть числом'
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id={ingredient_id} не найден'
                )
            if not amount or amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
            ingredient_ids.append(ingredient_id)
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
        for tag_id in value:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'Тег с id={tag_id} не найден'
                )
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Название обязательно')
        if len(value) > MAX_LEN_NAME:
            raise serializers.ValidationError(
                f'Название не должно превышать {MAX_LEN_NAME} символов'
            )
        return value

    def validate_text(self, value):
        if not value:
            raise serializers.ValidationError('Описание обязательно')
        return value

    def validate_cooking_time(self, value):
        if not value or value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не менее 1 минуты'
            )
        return value

    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get('image') and not self.initial_data.get('image'):
                raise serializers.ValidationError(
                    {'image': 'Изображение обязательно'}
                )
            ingredients_data = self.initial_data.get('ingredients')
            if 'ingredients' not in self.initial_data or not ingredients_data:
                raise serializers.ValidationError(
                    {'ingredients': 'Обязательное поле.'}
                )
            tags_data = self.initial_data.get('tags')
            if 'tags' not in self.initial_data or not tags_data:
                raise serializers.ValidationError(
                    {'tags': 'Обязательное поле.'}
                )
        if self.instance is not None:
            if 'ingredients' not in self.initial_data:
                raise serializers.ValidationError(
                    {'ingredients': 'Обязательное поле.'}
                )
            if 'tags' not in self.initial_data:
                raise serializers.ValidationError(
                    {'tags': 'Обязательное поле.'}
                )
        return attrs

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        request = self.context.get('request')
        recipe = Recipe.objects.create(
            author=request.user, **validated_data
        )
        recipe.tags.set(tags_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            self._save_ingredients(instance, ingredients_data)
        return instance


class ShortRecipeSerializer(RecipeImageMixin, serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit', MAX_AUTHOR_RECIPES)
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
