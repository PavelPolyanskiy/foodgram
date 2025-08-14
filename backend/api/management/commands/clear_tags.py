from django.core.management.base import BaseCommand

from recipe.models import Tag


class Command(BaseCommand):
    help = 'Очистка всех тэгов из БД'

    def handle(self, *args, **kwargs):
        ingredients = Tag.objects.all().delete()

        ingredients_after = Tag.objects.all()

        if len(ingredients) != len(ingredients_after):
            self.stdout.write(self.style.SUCCESS('Данные успешно удалены'))
        else:
            self.stdout.write(self.style.ERROR('Ошибка удаления данных'))
