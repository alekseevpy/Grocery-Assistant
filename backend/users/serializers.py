from core.serializers import FavoriteShoppingListSerializer
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):
    """Кастомный сериализатор для создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate(self, data):
        if self.initial_data.get("username") == ["me"]:
            raise serializers.ValidationError(
                {"username": "Вы не можете использовать этот username."}
            )
        return data


class UsersListSerializer(UserSerializer):
    """Cписок пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Follow.objects.filter(
                user=self.context["request"].user, author=obj
            ).exists()
        )


class SetPasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj["new_password"])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data["current_password"]):
            raise serializers.ValidationError(
                {"current_password": "Неверный пароль."}
            )
        if (
            validated_data["current_password"]
            == validated_data["new_password"]
        ):
            raise serializers.ValidationError(
                {"new_password": "Введите НОВЫЙ пароль."}
            )
        instance.set_password(validated_data["new_password"])
        instance.save()
        return validated_data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return bool(obj.following.filter(user=user))

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get(
            "recipes_limit", settings.RECIPES_DEFAULT
        )
        recipes = obj.recipe.all()[: int(limit)]
        return FavoriteShoppingListSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на автора."""

    class Meta:
        model = Follow
        fields = (
            "id",
            "user",
            "author",
        )

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны на этого пользователя.",
            )
        ]

    def validate(self, data):
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя."
            )
        return data
