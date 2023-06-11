from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель Пользователя."""

    email = models.EmailField(
        "Адрес электронной почты", max_length=254, unique=True
    )
    username = models.CharField(
        "Уникальный юзернейм", max_length=150, unique=True
    )
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    password = password = models.CharField("Пароль", max_length=150)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
