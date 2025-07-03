import base64
import datetime as dt

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from recipe.models import Recipe, Tag, TagToRecipe, Ingredient


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
    id = serializers.SerializerMethodField('get_id', read_only=True)
    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'password', 'avatar', 'is_subscribed'
        ]

    def get_id(self, obj):
        return obj.pk

    def get_avatar_url(self, obj): # возвращает немного не то что нужно ааааааааааааааааааааааааааааааааааа "avatar": "http://foodgram.example.org/media/users/default_avatar.png"
        if obj.avatar:
            return obj.avatar.url
        return None

class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
    

class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, write_only=True)
    current_password = serializers.CharField(max_length=150, write_only=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserMeSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')


    
