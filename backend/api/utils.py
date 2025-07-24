import base64
from pathlib import Path

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import FileResponse

from recipe.models import ShoppingCart, IngredientRecipe


class Base64ImageField(serializers.ImageField):
    """Конвертируем строку Base64 в изображение."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShoppingCartDownloader:
    """Класс для создания файла с ингредиентами и его скачивания."""

    @staticmethod
    def download_shopping_list(request):
        dir_path = Path(settings.MEDIA_ROOT) / 'shopping_cart'
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f'{request.user}_shopping_list.txt'
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients_dict = {}
        for item in shopping_cart:
            items_queryset = IngredientRecipe.objects.filter(
                recipe=item.recipe
            )
            for el in items_queryset:
                key = (el.ingredient.name, el.ingredient.measurement_unit)
                if key in ingredients_dict:
                    ingredients_dict[key] += el.amount
                else:
                    ingredients_dict[key] = el.amount

        with open(file_path, 'w', encoding='utf-8') as file:
            for key, value in ingredients_dict.items():
                file.write(f'{key[0]} - {value} {key[1]} \n')
        response = FileResponse(
            open(file_path, 'rb'), as_attachment=True,
            filename=f'{request.user}_shopping_list.txt'
        )
        return response
