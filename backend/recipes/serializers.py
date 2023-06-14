import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов с количеством в рецепте."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "number")


class IngredientRecipeSaveSerializer(serializers.ModelSerializer):
    """Сериализатор для сохранения ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientRecipe
        ields = ("id", "number")


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class Base64ImageField(serializers.ImageField):
    """Сериализатор декодирования картинки."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    def __init__(self, *args, **kwargs):
        super(RecipeSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        self.fields["author"].context["request"] = request

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="ingredientrecipe_set"
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and bool(obj.lover.filter(user=user))

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and bool(obj.buyer.filter(user=user))


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = IngredientRecipeSaveSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "author",
            "ingredients",
        )
        read_only_fields = (
            "author",
            "ingredients",
        )

    def to_representation(self, value):
        return RecipeSerializer(value, context=self.context).data

    def create(self, validated_data):
        tags_list = validated_data.pop("tags")
        ingredient_list = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for item in ingredient_list:
            ingredient = get_object_or_404(Ingredient, id=item.get("id"))
            IngredientRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=item.get("amount")
            )
        for item in tags_list:
            TagRecipe.objects.create(tag=item, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get("image") is not None:
            instance.image = validated_data.pop("image")
        instance.name = validated_data.get("name")
        instance.text = validated_data.get("text")
        instance.cooking_time = validated_data.get("cooking_time")

        tags_list = validated_data.pop("tags")
        instance.tags.set(tags_list)

        ingredient_list = validated_data.pop("ingredients")
        instance.ingredients.clear()
        for item in ingredient_list:
            ingredient = get_object_or_404(Ingredient, id=item.get("id"))
            instance.ingredients.add(
                ingredient, through_defaults={"amount": item.get("amount")}
            )

        instance.save()
        return instance
