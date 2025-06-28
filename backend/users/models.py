from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator, validate_username_me


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, validate_username_me],
        verbose_name='Имя пользователя'
    )

    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default='users/default_avatar.png',
        verbose_name='Аватар пользователя'
    )

    is_subscribed = models.BooleanField(default=False, verbose_name='Подписан')

    def __str__(self):
        return self.username

    # подписки и избранное