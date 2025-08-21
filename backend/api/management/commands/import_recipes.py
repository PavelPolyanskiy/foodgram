import json
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from recipe.models import Ingredient, Recipe, IngredientRecipe, Tag


User = get_user_model()


class Command(BaseCommand):
    fake_image = ''
    author = None
    users = User.objects.all()

    def get_author(self):
        return random.choice(self.users)

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/recipes.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        try:
            for recipe_data in data:
                self._create_recipe(recipe_data)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

    def _create_user(self):
        User.objects.create(
            email='chef@foodgram.ru',
            username='autochef',
            first_name='Повар',
            last_name='Шеф'
        )

    def _create_recipe(self, recipe_data):
        if not self.users.exists():
            self._create_user()
            self.users = User.objects.all()

        tags = recipe_data.pop('tags')
        ingredients = recipe_data.pop('ingredients')
        recipe_name = recipe_data['name']

        if Recipe.objects.filter(name=recipe_name).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Рецепт {recipe_name!r} уже существует! Пропускаем.'
                )
            )
            return

        try:
            with transaction.atomic():
                recipe, created = Recipe.objects.update_or_create(
                    author=self.get_author(),
                    defaults=recipe_data
                )

                tag_objects = Tag.objects.filter(id__in=tags)
                recipe.tags.set(tag_objects)

                for ingredient in ingredients:

                    ingredient_id = ingredient['id']
                    if not Ingredient.objects.filter(
                        id=ingredient_id
                    ).exists():
                        raise ValueError(
                            f'Ингредиент с ID {ingredient_id} не существует!'
                        )

                    current_ingredient = Ingredient.objects.get(
                        id=ingredient_id
                    )
                    IngredientRecipe.objects.create(
                        recipe=recipe,
                        ingredient=current_ingredient,
                        amount=ingredient['amount'],
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно создан рецепт {recipe_name!r}!'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при создании рецепта {recipe_name}: {str(e)}'
                )
            )
