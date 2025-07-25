from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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
        #default='users/default_avatar.png', # TODO 
        verbose_name='Аватар пользователя'
    )

    follows = models.ManyToManyField(
        'self',
        through='Follow',
        related_name='followers',
        symmetrical=False,
        verbose_name='Подписки'
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
