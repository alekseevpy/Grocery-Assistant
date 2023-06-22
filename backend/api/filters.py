from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для представления рецептов."""

    is_favorited = filters.NumberFilter(
        field_name="favorite__user",
        method="filter_users_lists",
        label="is_favorited",
    )
    is_in_shopping_cart = filters.NumberFilter(
        field_name="shopping_list__user",
        method="filter_users_lists",
        label="is_in_shopping_cart",
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_users_lists(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not int(value):
            return queryset
        return queryset.filter(**{name: user})
