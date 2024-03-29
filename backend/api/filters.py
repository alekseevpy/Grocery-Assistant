from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method="is_favorite_filter")
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_list_filter"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    def is_favorite_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_list_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_list__user=user)
        return queryset
