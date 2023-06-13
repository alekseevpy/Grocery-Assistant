from core.html_to_pdf import html_to_pdf
from core.models import Favorite, ShoppingList
from core.paginators import CustomPagination
from core.permissions import IsAuthorOrReadOnly
from core.serializers import (FavoriteCreateSerializer,
                              ShoppingListCreateSerializer)
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from recipes.serializers import (IngredientSerializer, RecipeCreateSerializer,
                                 RecipeSerializer, TagSerializer)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для:
    - получения списка тегов;
    - получения информации о конкретном теге."""

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPagination


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для:
    - получения списка ингридиентов с возможностью поиска по имени;
    - получения информации о конкретном ингридиенте."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "create", "delete"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        if self.action == "favorite":
            return FavoriteCreateSerializer
        if self.action == "shopping_cart":
            ShoppingListCreateSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        elif self.action in ("favorite", "shopping_cart"):
            self.permission_classes = (IsAuthenticated,)
        elif self.request.method in ("PATCH", "DELETE"):
            self.permission_classes = (IsAuthorOrReadOnly,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = RecipeSerializer(
                recipe, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"errors": "Рецепт уже в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            get_object_or_404(
                Favorite, user=request.user, recipe=recipe
            ).delete()
            return Response(
                {"detail": "Рецепт удален из избранного."},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=True,
        methods=["post", "delete"],
        pagination_class=None,
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = RecipeSerializer(
                recipe, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not ShoppingList.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                ShoppingList.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"errors": "Рецепт уже в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            get_object_or_404(
                ShoppingList, user=request.user, recipe=recipe
            ).delete()
            return Response(
                {"detail": "Рецепт удален из списка покупок."},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        methods=["get"],
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        context = user.shopping_list.values(
            "recipe__ingredients__name",
            "recipe__ingredients__measurement_unit",
        ).annotate(total=Sum("recipe__ingredientrecipe__amount"))
        return html_to_pdf("shopinglisttopdf.html", {"context": context})
