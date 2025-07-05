import base64
import datetime as dt

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework import serializers

from recipe.models import Recipe, Tag, IngredientRecipe, Ingredient
from users.models import Follow


User = get_user_model()


class Base64ImageField(serializers.ImageField): ## убрать в core или еще куда           ав
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для логики эндпоинта /users/.""" # //////////////////////////

    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Эта электронная почта '
                'уже используется.'
            )
        ]
    )

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Это имя уже используется.'
            )
        ]
    )

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, write_only=True) # прикрути валидациююююююююююююююююююю

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name',
            'last_name', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Использовать имя me запрещено.')
        return value
  

class UserMeSerializer(UserSignUpSerializer):
    """Сериализатор для логики эндпоинта /me/ ."""

    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar',
        ]

    def get_is_subscribed(self, obj):
        return 1 == 1                           # заглушка

    def get_avatar_url(self, obj): # возвращает немного не то что нужно ааааааааааааааааааааааааааааааааааа "avatar": "http://foodgram.example.org/media/users/default_avatar.png"
        if obj.avatar:
            return obj.avatar.url
        return None                   


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
    

class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, max_length=150, write_only=True)
    current_password = serializers.CharField(required=True, max_length=150, write_only=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(required=False, min_value=1, max_value=1000)
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, max_value=1000)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientInRecipeSerializer1(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    # id = serializers.ReadOnlyField()
    # name = serializers.ReadOnlyField()
    # measurement_unit = serializers.ReadOnlyField()
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        # Для случая, когда obj - это IngredientRecipe (промежуточная модель)
        if hasattr(obj, 'amount'):
            return obj.amount

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
    


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserMeSerializer()
    ingredients = IngredientInRecipeSerializer1(many=True, source='ingredientrecipe_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        return 1 == 1                                                 # заглушки пока что
    
    def get_is_in_shopping_cart(self, obj):
        return 1 == 1

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time']


class RecipeCreateSerializer(serializers.ModelSerializer):
    
    ingredients = IngredientRecipeSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(allow_null=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault()) # задумайся?????

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')

    # def validate_ingredients(self, value):
    #     if not value:
    #         raise ValidationError('Добавьте минимум 1 ингредиент.')
    #     seen = set()
    #     for item in value:
    #         ingredient = item['id']
    #         if ingredient in seen:
    #             raise ValidationError(f'Ингредиент {ingredient} повторяется.')
    #         seen.add(ingredient)
    #     return value
    # def validate_ingredients(self, value):
    #     if not value:
    #         raise ValidationError('Добавьте минимум 1 ингредиент.')
    #     return value

    # def validate_tags(self, value):
    #     if not value:
    #         raise ValidationError('Добавьте минимум 1 тег.')
        
        # return value

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
                ingredient=ingredient['id'],  # объект Ingredient
                amount=ingredient['amount']
            )

        for tag in tags:
            recipe.tags.add(tag)
        return recipe
 
    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data




class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор модели Follow."""

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Нельзя подписаться на самого себя'
            )
        ]

    def validate_following(self, value):
        """Проверка, что пользователь не может подписаться на самого себя."""
        if self.context.get('request').user == value:
            raise ValidationError('Нельзя подписаться на самого себя.')
        return value
