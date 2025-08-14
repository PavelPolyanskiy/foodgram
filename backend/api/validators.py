from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Недопустимые символы в имени',
    code='invalid_username'
)
