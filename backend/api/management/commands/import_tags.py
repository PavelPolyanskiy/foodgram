import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipe.models import Tag


class Command(BaseCommand):
    help = 'Импорт данных из JSON файлов'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'data')

        file_data = self.__get_data_from_file(data_dir, 'tags.json')
        for el in file_data:
            Tag.objects.update_or_create(
                name=el['name'],
                slug=el['slug']
            )

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))

    def __get_data_from_file(self, data_dir, file_name):
        with open(
            file=os.path.join(data_dir, file_name),
            encoding='utf-8'
        ) as file:
            data = json.load(file)
        return data
