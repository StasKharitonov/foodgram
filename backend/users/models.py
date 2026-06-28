from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.validators import namevalidator
from recipes.constants import MAX_LEN_EMAIL, MAX_LEN_USERNAME

from .managers import CustomUserManager


class Role(models.TextChoices):
    USER = 'user', 'Пользователь'
    AUTH_USER = 'auth_user', 'Аутентифицированный пользователь'
    ADMIN = 'admin', 'Администратор'


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
            namevalidator,
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
    role = models.CharField(
        max_length=max(len(role) for role, _ in Role.choices),
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_auth_user(self):
        return self.role == Role.AUTH_USER

    def __str__(self):
        return self.username
