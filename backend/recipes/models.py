from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

from .constants import (MAX_COOKING_TIME, MAX_LEN_INGREDIENT_NAME,
                        MAX_LEN_MEASURE, MAX_LEN_RECIPE_NAME, MAX_LEN_TAG,
                        MAXIMUM_WORD_LENGTH, MIN_COOKING_TIME,
                        MIN_INGREDIENT_AMOUNT)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        'Название',
        max_length=MAX_LEN_RECIPE_NAME
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message=(
                    f'Время приготовления должно быть '
                    f'не менее {MIN_COOKING_TIME} минуты'
                ),
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=(
                    f'Время приготовления не должно превышать '
                    f'{MAX_COOKING_TIME} минут'
                ),
            ),
        )
    )
    created_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        if len(self.name) > MAXIMUM_WORD_LENGTH:
            return f'{self.name[:MAXIMUM_WORD_LENGTH]}'
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LEN_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEN_MEASURE
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_name_unit',
            ),
        )

    def __str__(self):
        if len(self.name) > MAXIMUM_WORD_LENGTH:
            return self.name[:MAXIMUM_WORD_LENGTH]
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LEN_TAG,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_LEN_TAG,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        if len(self.name) > MAXIMUM_WORD_LENGTH:
            return self.name[:MAXIMUM_WORD_LENGTH]
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=(
                    f'Количество ингредиента должно быть '
                    f'не менее {MIN_INGREDIENT_AMOUNT}'
                ),
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        ingredient_name = self.ingredient.name
        if len(ingredient_name) > MAXIMUM_WORD_LENGTH:
            return f'{ingredient_name[:MAXIMUM_WORD_LENGTH]}'
        return ingredient_name


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique_user_recipe',
            ),
        )

    def __str__(self):
        return f'{self.recipe} — {self._meta.verbose_name} ({self.user})'


class Favorite(UserRecipe):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipe):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
