from django.core.management.base import BaseCommand

from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Очистка всех ингредиентов из БД'

    def handle(self, *args, **kwargs):
        ingredients = Ingredient.objects.all().delete()

        ingredients_after = Ingredient.objects.all()

        if len(ingredients) != len(ingredients_after):
            self.stdout.write(self.style.SUCCESS('Данные успешно удалены'))
        else:
            self.stdout.write(self.style.ERROR('Ошибка удаления данных'))
