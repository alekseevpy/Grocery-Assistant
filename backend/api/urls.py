from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    DownloadShoppingCartView,
)

app_name = "api"
router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path(
        "recipes/<int:recipe_id>/favorite/",
        FavoriteViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="favorite_recipe",
    ),
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        ShoppingCartViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="shopping_cart",
    ),
    path(
        "recipes/download_shopping_cart/",
        DownloadShoppingCartView.as_view(),
        name="download_shopping_cart",
    ),
    path("", include(router.urls)),
]
