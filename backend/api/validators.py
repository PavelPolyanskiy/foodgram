from django.core.validators import RegexValidator
from rest_framework.validators import ValidationError
from .constants import MIN_PASSWORD_LENGTH


def password_validator(value):
    if (
        value.isdigit()
        or value.isalpha()
        or len(value) < MIN_PASSWORD_LENGTH
    ):
        raise ValidationError(
            'Пароль должен состоять из цифр И букв, '
            'а так же быть длиннее 7 символов.'
        )


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Недопустимые символы в имени',
    code='invalid_username'
)