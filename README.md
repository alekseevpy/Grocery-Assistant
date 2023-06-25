![foodgram-project-react Workflow Status](https://github.com/alekseevpy/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)
# Продуктовый помощник Foodgram - дипломный проект студента 51 когорты Яндекс.Практикум.

## Описание проекта Foodgram
«Продуктовый помощник»: сервис, на котором пользователи публикуют рецепты кулинарных изделий, подписываются на публикации других авторов и добавляют рецепты в своё избранное.
Сервис «Список покупок» позволит пользователю создать список продуктов, которые нужно купить для приготовления выбранных блюд согласно рецептам.

## Установка

1. Проверить наличие Docker

   Прежде чем приступать к работе, убедиться что Docker установлен, для этого ввести команду:

   ```bash
   docker -v
   ```

   В случае отсутствия, скачать [Docker Desktop](https://www.docker.com/products/docker-desktop) для Mac или Windows. [Docker Compose](https://docs.docker.com/compose) будет установлен автоматически.

   В Linux проверить, что установлена последняя версия [Compose](https://docs.docker.com/compose/install/).

   Также можно воспользоваться официальной [инструкцией](https://docs.docker.com/engine/install/).

2. Клонировать репозиторий на локальный компьютер

   ```bash
   git clone https://github.com/alekseevpy/foodgram-project-react.git
   ```

3. В корневой директории создать файл `.env`, согласно примеру:

   ```bash
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ```

4. Запустить `docker-compose`

   Выполнить из корневой директории команду:

   ```bash
   docker-compose up -d
   ```

5. Заполнить БД

   Создать и выполнить миграции:

   ```bash
   docker-compose exec web python manage.py makemigrations --noinput
   docker-compose exec web python manage.py migrate --noinput
   ```

6. Подгрузить статику

   ```bash
   docker-compose exec web python manage.py collectstatic --no-input
   ```

7. Заполнить БД тестовыми данными

   1. Войдите в контейнер backend. Для этого выполните следующую команду:

   ```bash
    docker-compose exec backend bash
    ```

    2. Внутри контейнера backend выполните команду:

    ```bash
    python manage.py fill_my_bd_ingridients
    ```

8. Создать суперпользователя

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

9. Остановить работу всех контейнеров

   ```bash
   docker-compose down
   ```

10. Пересобрать и запустить контейнеры

    ```bash
    docker-compose up -d --build
    ```

11. Мониторинг запущенных контейнеров

    ```bash
    docker stats
    ```

12. Остановить и удалить контейнеры, тома и образы

    ```bash
    docker-compose down -v
    ```

## Ссылки

Проект будет доступен по следующей ссылке <http://158.160.10.25/recipes/>  
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
