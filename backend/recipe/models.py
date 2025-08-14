import random
import string

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from api.constants import NAME_LENGTH, SHORT_LINK_LENGTH, SLUG_LENGTH

User = get_user_model()


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        max_length=NAME_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    slug = models.SlugField(
        max_length=SLUG_LENGTH,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиент."""

    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Единица измерения для ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None
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
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date', )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Промежуточная таблица для ingredient и recipe."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients'
    )

    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return (
            f'{self.ingredient},'
            f'{self.amount}, {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Модель избранного."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'

    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_carts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_carts'

    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'


def create_random_string():
    symbols = string.ascii_letters + string.digits
    return ''.join(random.choice(symbols) for _ in range(SHORT_LINK_LENGTH))


class RecipeShortLink(models.Model):
    """Модель для коротких ссылок рецептов."""

    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link'
    )

    short_link = models.CharField(
        max_length=SHORT_LINK_LENGTH,
        verbose_name='Короткая ссылка',
        default=create_random_string,
        unique=True
    )

    class Meta:
        verbose_name = 'Модель коротких ссылок'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.recipe} ---> {self.short_link}'
