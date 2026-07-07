from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import MAX_LEN_EMAIL, MAX_LEN_USERNAME


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField(
        max_length=MAX_LEN_EMAIL,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=MAX_LEN_USERNAME,
        unique=True,
        verbose_name='Псевдоним',
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя юзера может содержать следующие символы: @.+-_'
            ),
        )
    )
    first_name = models.CharField(
        max_length=MAX_LEN_USERNAME,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_LEN_USERNAME,
        verbose_name='фамилия',
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscriptions',
        verbose_name='Автор',
    )

    class Meta:
        db_table = 'recipes_subscription'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_name_owner',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription',
            ),
        )

    def clean(self):
        super().clean()
        if self.user_id == self.author_id:
            raise ValidationError('Нельзя подписаться на самого себя')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
