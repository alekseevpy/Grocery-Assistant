from django.db import models

from recipes.models import Recipe
from users.models import User


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Избранный рецепт",
    )

    class Meta:
        verbose_name = "Список избранных рецептов"
        verbose_name_plural = "Списки избранных рецептов"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorites"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} сохранил "
            f"в избранное рецепт {self.recipe.name}"
        )


class ShoppingList(models.Model):
    """Модель cписка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Список покупок",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shoppinglist"
            )
        ]

    def __str__(self):
        ingredients_list = ", ".join(
            str(ingredient) for ingredient in self.recipe.ingredients.all()
        )
        return (
            f"{self.user.username} планирует купить эти ингредиенты:"
            f"{ingredients_list}"
        )
