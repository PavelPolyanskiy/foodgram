import base64
from io import BytesIO

from rest_framework import serializers
from django.core.files.base import ContentFile
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

        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients_dict = {}
        for cart_item in shopping_cart:
            recipe_ingredients = IngredientRecipe.objects.filter(
                recipe=cart_item.recipe
            )

            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                key = (ingredient.name, ingredient.measurement_unit)
                amount = recipe_ingredient.amount

                if key in ingredients_dict:
                    ingredients_dict[key] += amount
                else:
                    ingredients_dict[key] = amount

        head = [
            f'Список покупок {request.user.username}\n\n',
            f'Количество рецептов в списке: {len(shopping_cart)}\n\n',
            'Список ингредиентов к покупке:\n\n',
        ]

        shop_list = []
        for key, value in ingredients_dict.items():
            shop_list.append(f'{key[0]} - {value} {key[1]} \n')

        response = '\n'.join(head + shop_list)
        byte_response = BytesIO(response.encode('utf-8'))

        return FileResponse(
            byte_response,
            as_attachment=True,
            filename='Shopping_list.txt',
            content_type='text/plain'
        )
