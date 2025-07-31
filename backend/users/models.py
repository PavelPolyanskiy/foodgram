from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator, validate_username_me
from api.constants import (MAX_EMAIL_LENGTH, USERNAME_LENGTH,
                           FIRST_NAME_LENGTH, LAST_NAME_LENGTH)


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Данный эл. адрес уже используется',
        },
        max_length=MAX_EMAIL_LENGTH
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        validators=[username_validator, validate_username_me],
        error_messages={
            'unique': 'Данное имя пользователя уже используется',
        },
        max_length=USERNAME_LENGTH,
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

    # follows = models.ManyToManyField(  # не работает должным образом, лучше отд. модель
    #     'self',
    #     through='Follow',
    #     related_name='followers',
    #     symmetrical=False,
    #     verbose_name='Подписки'
    # )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )

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
