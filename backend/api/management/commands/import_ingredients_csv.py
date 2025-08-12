import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'data')

        file_data = self.__get_data_from_file(data_dir, 'ingredients.csv')
        for row in file_data:
            Ingredient.objects.update_or_create(
                name=row['name'],
                defaults={'measurement_unit': row['measurement_unit']}
            )

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))

    def __get_data_from_file(self, data_dir, file_name):
        with open(
            file=os.path.join(data_dir, file_name),
            encoding='utf-8'
        ) as file:
            data = list(csv.DictReader(file))
        return data
