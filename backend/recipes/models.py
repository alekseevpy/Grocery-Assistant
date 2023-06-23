from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель для тега."""

    name = models.CharField("Название", max_length=200, unique=True)
    color = models.CharField("Цвет в HEX", max_length=7, unique=True)
    slug = models.SlugField("Уникальный слаг", max_length=200, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингридиента."""

    name = models.CharField("Название", max_length=200, db_index=True)
    measurement_unit = models.CharField("Единица измерения", max_length=200)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        through="TagRecipe",
        verbose_name="Теги рецепта",
    )
    image = models.ImageField("Картинка", upload_to="recipes/images/")
    name = models.CharField("Название", max_length=200, db_index=True)
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (мин)"
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Промежуточная модель связи ингредиента в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField("Количество")

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.ingredient.name} объявлен в {self.recipe.name}"


class TagRecipe(models.Model):
    """Промежуточная модель связи тега и рецепта."""

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Тег и рецепт"
        verbose_name_plural = "Теги и рецепты"

    def __str__(self):
        return f"{self.tag.name} добавлен к рецепту: {self.recipe.name}"
