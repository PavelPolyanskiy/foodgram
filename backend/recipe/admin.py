from django.contrib import admin
from .models import (Tag, Ingredient, Recipe,
                     IngredientRecipe, Favorite,
                     ShoppingCart, RecipeShortLink)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'pub_date')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

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

@admin.register(RecipeShortLink)
class RecipeShortLinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'short_link')
