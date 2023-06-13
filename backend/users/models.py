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


class Follow(models.Model):
    """Модель подписки пользователя на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="self-subscription_avoidance",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
