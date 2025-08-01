from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserSerializer
from djoser.serializers import SetPasswordSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from recipe.models import (Recipe, Tag, IngredientRecipe,
                           Ingredient, Favorite, ShoppingCart)
from users.models import Follow
from .utils import Base64ImageField
from .constants import (MAX_EMAIL_LENGTH, MAX_FIELD_LENGTH, MIN_ING_AMOUNT,
                        MAX_ING_AMOUNT)

import pprint

User = get_user_model()


class UserCreateSerializer(DjoserUserSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class UserSerializer(UserCreateSerializer):
    """Сериализатор для списка пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj
            ).exists()

        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar', )

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar')
        instance.save()
        return instance

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=1000
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_ING_AMOUNT, max_value=MAX_ING_AMOUNT
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientInRecipeSerializer1(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        return obj.amount

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer1(
        many=True, source='recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:

            return Favorite.objects.filter(
                recipe=obj, user=request.user
            ).exists()

        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')

        if request.user.is_authenticated:

            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()

        return False

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):

    ingredients = IngredientRecipeSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(allow_null=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, value):

        if not value:
            raise ValidationError('Добавьте минимум 1 ингредиент.')

        ingredients = set()
        for item in value:
            ingredient = item.get('id')
            if ingredient in ingredients:
                raise ValidationError(f'Ингредиет {ingredient} повторяется.')
            ingredients.add(ingredient)

        return value

    def validate_tags(self, value):

        if not value:
            raise ValidationError('Добавьте минимум 1 тег.')

        tags = set()
        for tag in value:
            if tag in tags:
                raise ValidationError(f'Тег {tag} повторяется.')
            tags.add(tag)

        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError('Время готовки не может быть меньше 1 мин.')

        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

        for tag in tags:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):

        ingredients = validated_data.pop('ingredients', [])
        if not ingredients:
            raise ValidationError({'message': 'Добавьте минимум 1 ингредиент.'})
        tags = validated_data.pop('tags', [])
        if not tags:
            raise ValidationError({'message': 'Добавьте минимум 1 тег.'})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.tags.clear()

        for tag in tags:
            instance.tags.add(tag)

        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe для возврата краткой информации о рецетпте.

    Используется в FavoriteSerializer.

    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для эндпоинта /users/subscriptions/ ."""

    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipe_count', 'avatar'
        )

    def get_recipes(self, obj):
        user_recipes = obj.recipes.all()
        return RecipeFavoriteSerializer(
            user_recipes, many=True, context=self.context
        ).data

    def get_recipe_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор модели Follow."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Follow.objects.all(),
        #         fields=('user', 'following'),
        #         message='Нельзя подписаться на самого себя'
        #     )
        # ]

    def validate_following(self, value):
        """Проверка, что подписка уникальна."""
        if self.context.get('request').user == value:
            raise ValidationError('Нельзя подписаться на самого себя.')

        return value

    def create(self, validated_data):
        user = self.context.get('request').user
        following = validated_data.get('following')
        if Follow.objects.filter(user=user, following=following).exists():
            raise ValidationError(
                {'message': 'Вы уже подписаны на этого пользователя.'}
            )

        return Follow.objects.create(user=user, following=following)

    def to_representation(self, instance):

        return SubscriptionsSerializer(
            instance.user,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""

    class Meta:
        model = Favorite
        fields = ('id', 'recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        ]

    def to_representation(self, instance):
        return RecipeFavoriteSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с корзиной покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в корзине покупок.'
            )
        ]
    
    def to_representation(self, instance):
        return RecipeFavoriteSerializer(instance.recipe).data
