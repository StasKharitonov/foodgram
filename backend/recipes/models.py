from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .constants import (
    MAX_LEN_INGREDIENT_NAME,
    MAX_LEN_MEASURE,
    MAX_LEN_RECIPE_NAME,
    MAX_LEN_TAG,
    MAXIMUM_WORD_LENGTH,
)


class CreatedAtAbstract(models.Model):
    created_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class Recipe(CreatedAtAbstract):
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
        null=False,
        blank=False
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
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления должно быть не менее 1 минуты'
            )
        ]
    )

    class Meta(CreatedAtAbstract.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

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
        'Количество'
    )

    def __str__(self):
        ingredient_name = self.ingredient.name
        if len(ingredient_name) > MAXIMUM_WORD_LENGTH:
            return f'{ingredient_name[:MAXIMUM_WORD_LENGTH]}'
        return ingredient_name

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            ),
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_items',
        verbose_name='Пользователь'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине пользователя {self.user}'


class Subscription(CreatedAtAbstract):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribed_to}'

    class Meta(CreatedAtAbstract.Meta):
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'subscribed_to'),
                name='unique_name_owner'
            ),
        )
