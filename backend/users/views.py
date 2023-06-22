from core.paginators import CustomPagination
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import (
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
    UserRegistrationSerializer,
    UsersListSerializer,
)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для:
    - регистрации нового пользователя;
    - получения списка пользователей;
    - получения информации о конкретном пользователе;
    - получения информации об авторизированном пользователе (/users/me/);
    - изменения пароля;
    - списка авторов, на которых подписан пользователь;
    - подписки на автора;
    - отписки от автора."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return UsersListSerializer
        return UserRegistrationSerializer

    @action(
        detail=False,
        methods=["get"],
        pagination_class=None,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UsersListSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["post"], permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {"detail": "Пароль успешно изменен."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs["pk"])

        if request.method == "POST":
            data = {"user": request.user.id, "author": author.id}
            sub_serializer = SubscriptionCreateSerializer(
                data=data,
                context={"request": request},
            )
            sub_serializer.is_valid(raise_exception=True)
            follow = sub_serializer.save()
            serializer = SubscriptionSerializer(
                follow.author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            get_object_or_404(
                Follow, user=request.user, author=author
            ).delete()
            return Response(
                {"detail": "Вы отписались от автора."},
                status=status.HTTP_204_NO_CONTENT,
            )
