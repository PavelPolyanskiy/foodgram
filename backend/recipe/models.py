from django.db import models
from django.contrib.auth import get_user_model

from .constants import UNIT_LENGTH, SLUG_LENGTH

User = get_user_model()


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        max_length=UNIT_LENGTH,
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
    """Ингредиент."""

    name = models.CharField(
        max_length=UNIT_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=UNIT_LENGTH,
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
        max_length=UNIT_LENGTH,
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
        through='IngredientToRecipe',
        verbose_name='Ингредиенты для рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagToRecipe',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    # is_favorited = models.ForeignKey(
    #     'Favorite',
    #     on_delete=models.CASCADE
    # )

    # is_in_shopping_cart = models.BooleanField(
    #     default=False,
    #     verbose_name='В списке покупок'
    # )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagToRecipe(models.Model):
    """Промежуточная таблица tag и recipe."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientToRecipe(models.Model):
    """Промежуточная таблица для ingredient и recipe."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    is_favorited = models.BooleanField(default=False) # надо ли???????
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Favorite'
    )
    user = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Favorited'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные' # дичь, достаточно vb без plural


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    is_in_shopping_cart = models.BooleanField(default=False) # надо ли???????????????
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Shopping'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Shoppings')

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
