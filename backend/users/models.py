from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import MAX_LEN_EMAIL, MAX_LEN_USERNAME


class User(AbstractUser):
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
    bio = models.TextField('Биография', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    created_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        db_table = 'recipes_subscription'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created_at',)
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'subscribed_to'),
                name='unique_name_owner',
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscribed_to')),
                name='prevent_self_subscription',
            ),
        )

    def clean(self):
        super().clean()
        if self.subscriber_id == self.subscribed_to_id:
            raise ValidationError('Нельзя подписаться на самого себя')

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribed_to}'
