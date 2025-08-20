from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import (FIRST_NAME_LENGTH, LAST_NAME_LENGTH)


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Данный эл. адрес уже используется',
        }
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_LENGTH
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_LENGTH
    )

    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )

    def __str__(self):
        return f'Пользователь: {self.username}'


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Кто'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='На кого'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('user__username', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
