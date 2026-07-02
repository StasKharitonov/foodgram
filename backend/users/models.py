from django.contrib.auth.models import AbstractUser
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
