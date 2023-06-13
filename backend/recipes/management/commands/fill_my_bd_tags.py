from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = "Создаем тэги"

    def handle(self, *args, **kwargs):
        data = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
            {"name": "Обед", "color": "#49B64E", "slug": "dinner"},
            {"name": "Ужин", "color": "#8775D2", "slug": "supper"},
            {"name": "Полдник", "color": "#2f2042", "slug": "poldnik"},
            {
                "name": "Второй ужин",
                "color": "#baacc7",
                "slug": "second_supper",
            },
        ]

        for tag_data in data:
            tag_name = tag_data["name"]

            try:
                tag = Tag.objects.get(name=tag_name)
                self.stdout.write(
                    f"Тег '{tag_name}' уже существует в базе данных"
                )
            except Tag.DoesNotExist:
                tag = Tag.objects.create(**tag_data)
                self.stdout.write(f"Тег '{tag_name}' был создан")

        self.stdout.write(self.style.SUCCESS("Все тэги загружены!"))
