from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Favorite, ShoppingList


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Этот рецепт уже есть в вашем списке.",
            )
        ]


class FavoriteShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в списке избранного и списке покупок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("name", "image", "cooking_time")


class ShoppingListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingList
        fields = (
            "id",
            "user",
            "recipe",
        )

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=("user", "recipe"),
                message="Этот рецепт уже есть в вашем списке.",
            )
        ]
