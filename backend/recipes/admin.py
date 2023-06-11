from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientRecipe, TagRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    readonly_fields = ("measurement_unit",)

    def measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    measurement_unit.short_description = "Единица измерения"


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")
    readonly_fields = ("favorite_count",)
    inlines = (IngredientRecipeInline, TagRecipeInline)

    def favorite_count(self, instance):
        return instance.favorite.count()

    favorite_count.short_description = "Количество добавлений в избранное"
