from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=('Имя пользователя должно содержать только'
             ' буквы, цифры и символы @/./+/-/_'),
    code='invalid_username'
)


def validate_username_me(value):
    if value == 'me':
        raise ValidationError('Использовать имя "me" запрещено')
