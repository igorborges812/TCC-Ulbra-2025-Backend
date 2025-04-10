import json
from django.contrib import admin
from .models import Recipe, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('id',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'display_ingredients')
    search_fields = ('id', 'title', 'user__nickname', 'category__name')
    list_filter = ('category', 'user')
    ordering = ('id',)

    def display_ingredients(self, obj):
        try:
            ingredients = json.loads(obj.ingredients)
            return ", ".join([f"{ing['name']} ({ing['quantity']} {ing['unit']})" for ing in ingredients])
        except Exception as e:
            return f"Erro: {e}"

    display_ingredients.short_description = 'Ingredientes'