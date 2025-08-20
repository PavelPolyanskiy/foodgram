import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from api.constants import (RECIPE_NAME_LENGTH, SHORT_LINK_LENGTH,
                           TAG_NAME_LENGTH, TAG_SLUG_LENGTH, AMOUNT_MIN_VALUE,
                           ING_MU_LENGTH, ING_NAME_LENGTH,
                           COOKING_TIME_MIN_VALUE, INT_FIELD_MAX_VALUE)

User = get_user_model()


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        max_length=TAG_NAME_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_LENGTH,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'Тег: {self.name}'


class Ingredient(models.Model):
    """Модель ингредиент."""

    name = models.CharField(
        max_length=ING_NAME_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=ING_MU_LENGTH,
        verbose_name='Единица измерения ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_measurement_unit_combination'
            )
        ]

    def __str__(self):
        return (
            f'Ингредиент: {self.name}, '
            f'д. измерения: {self.measurement_unit}'
        )


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=RECIPE_NAME_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты для рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(COOKING_TIME_MIN_VALUE),
            MaxValueValidator(INT_FIELD_MAX_VALUE)
        ),
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=timezone.now
    )

    short_link = models.CharField(
        max_length=SHORT_LINK_LENGTH,
        verbose_name='Короткая ссылка',
        blank=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'Рецепт: {self.name}'

    def save(self, *args, **kwargs):
        if not self.pk:
            unique = False
            while not unique:
                self.short_link = self.create_random_string()
                unique = not Recipe.objects.filter(
                    short_link=self.short_link
                ).exists()
        super().save(*args, **kwargs)

    def create_random_string(self):
        symbols = string.ascii_letters + string.digits
        return ''.join(
            random.choice(symbols) for _ in range(SHORT_LINK_LENGTH)
        )


class IngredientRecipe(models.Model):
    """Промежуточная таблица для ingredient и recipe."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(AMOUNT_MIN_VALUE),
            MaxValueValidator(INT_FIELD_MAX_VALUE),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = verbose_name
        ordering = ('recipe__pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient_combination'
            )
        ]

    def __str__(self):
        return (
            f'В рецепте: {self.recipe.name} '
            f'Ингредиент: {self.ingredient.name} '
            f'Количество: {self.amount} '
            f'Ед. измерения ин-та.:{self.ingredient.measurement_unit} '
        )


class Favorite(models.Model):
    """Модель избранного."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='В избранном у'

    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user__username', )
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='В корзине у'

    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        ordering = ('user__username', )
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
