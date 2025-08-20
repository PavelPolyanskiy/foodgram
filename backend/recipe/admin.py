from django.contrib import admin
from django.utils.html import format_html

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from api.constants import ING_INLINE_MIN_VALUE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = ING_INLINE_MIN_VALUE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'cooking_time',
        'pub_date', 'get_favorite_count',
        'short_link', 'display_image'
    )
    search_fields = ('name', 'author__username')
    exclude = ('short_link',)
    list_filter = ('tags',)
    inlines = (IngredientRecipeInline, )

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    get_favorite_count.short_description = 'Количество добавлений в избранное'

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: auto;" />',
                obj.image.url
            )
        return 'Нет изображения'
    display_image.short_description = 'Изображение'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.short_link = obj.create_random_string()
        super().save_model(request, obj, form, change)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient__name', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')
