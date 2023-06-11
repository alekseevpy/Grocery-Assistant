from django.db import models
from users.models import User
from recipes.models import Recipe


class Subscription(models.Model):
    """Модель подписки пользователя на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="celebrity",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_couple"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="self-subscription_avoidance",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chooser",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Рецепт",
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
        related_name="buyer",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="stuff",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
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
