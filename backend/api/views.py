from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from core.html_to_pdf import html_to_pdf
from core.models import Favorite, ShoppingList
from core.paginators import CustomPagination
from core.permissions import IsAuthorOrReadOnly
from core.serializers import (
    FavoriteCreateSerializer,
    ShoppingListCreateSerializer,
)
from recipes.models import Ingredient, Recipe, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
)

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


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для:
    - получения списка ингридиентов с возможностью поиска по имени;
    - получения информации о конкретном ингридиенте."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        if not Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            {"errors": "Рецепт уже в избранном."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite.delete()
        return Response(
            {"detail": "Рецепт удален из избранного."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        serializer = ShoppingListCreateSerializer(
            data={"recipe": recipe.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if not ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"errors": "Рецепт уже в списке покупок."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["recipe_id"])
        shopping_list = get_object_or_404(
            ShoppingList, user=request.user, recipe=recipe
        )
        shopping_list.delete()
        return Response(
            {"detail": "Рецепт удален из списка покупок."},
            status=status.HTTP_204_NO_CONTENT,
        )


class DownloadShoppingCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        context = user.shopping_list.values(
            "recipe__ingredients__name",
            "recipe__ingredients__measurement_unit",
        ).annotate(total=Sum("recipe__ingredientrecipe__amount"))
        return html_to_pdf("shopinglisttopdf.html", {"context": context})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "create", "delete"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        elif self.request.method in ("PATCH", "DELETE"):
            self.permission_classes = (IsAuthorOrReadOnly,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
