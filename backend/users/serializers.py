# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
# from rest_framework.validators import UniqueValidator


# User = get_user_model()


# class UsernameEmailSreializer(serializers.Serializer):

#     username = serializers.RegexField(
#         regex=r'^[\w.@+-]+$',
#         max_length=150, # убери в константы хватит хардкодить ......................
#         required=True,
#     )
#     email = serializers.EmailField(required=True, max_length=254)

#     def validate_username(self, value):
#         if value == 'me':
#             raise ValidationError('Использовать имя me запрещено.')
#         return value


# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор для логики энжпоинта /users/.""" # //////////////////////////


#     email = serializers.EmailField(
#         max_length=254,
#         required=True,
#         validators=[
#             UniqueValidator(
#                 queryset=User.objects.all(),
#                 message='Эта электронная почта '
#                 'уже используется.'
#             )
#         ]
#     )

#     username = serializers.RegexField(
#         regex=r'^[\w.@+-]+$',
#         max_length=150,
#         required=True,
#         validators=[
#             UniqueValidator(
#                 queryset=User.objects.all(),
#                 message='Это имя уже используется.'
#             )
#         ]
#     )

#     first_name = serializers.CharField(max_length=150)
#     last_name = serializers.CharField(max_length=150)
#     password = serializers.CharField(max_length=150, write_only=True) # прикрути валидациююююююююююююююююююю

#     class Meta:
#         model = User
#         fields = [
#             'email', 'username', 'first_name',
#             'last_name', 'password'
#         ]

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user

#     def validate_username(self, value):
#         if value == 'me':
#             raise ValidationError('Использовать имя me запрещено.')
#         return value
  

# class UserMeSerializer(UserSerializer):
#     """Сериализатор для логики эндпоинта /me/ ."""

#     role = serializers.CharField(read_only=True)


# class SignUpSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = [
#             'email', 'username', 'first_name',
#             'last_name', 'password'
#         ]
    
#     def create(self, validated_data):
#         password = validated_data.pop('password') # pop а не get так как потом передаем 
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return User

