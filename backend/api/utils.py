import base64
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import FileResponse
from rest_framework import serializers

from recipe.models import IngredientRecipe, ShoppingCart


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

        ingredient_data = (
            IngredientRecipe.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by()  # так как в Meta модели прописан ordering
        )
        print(ingredient_data)

        recipes_amount = ShoppingCart.objects.filter(user=request.user).count()

        head = [
            f'Список покупок {request.user.username}\n\n',
            f'Количество рецептов в списке: {(recipes_amount)}\n\n',
            'Список ингредиентов к покупке:\n\n',
        ]

        shop_list = []

        for item in ingredient_data:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            shop_list.append(f'{name} - {amount} {unit} \n')

        response = ''.join(head + shop_list)
        byte_response = BytesIO(response.encode('utf-8'))

        return FileResponse(
            byte_response,
            as_attachment=True,
            filename='Shopping_list.txt',
            content_type='text/plain'
        )
