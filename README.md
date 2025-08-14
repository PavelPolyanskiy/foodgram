# Проект Foodgram

## Описание 

Данное веб-приложение позволяет читать и делиться рецептами, добавлять понравившиеся в избранное, а также подписываться на авторов рецептов.

Для удобства, есть возможность добавить рецепт(-ы) в корзину и скачать для них список покупок в .txt формате. 
В полученном списке будут все продукты, необходимые для приготовления рецепта(-ов), добавленных в корзину покупок. 
Повторяющиеся ингредиенты суммируются.

У проекта реализованы CI/CD  с помощью GitHub Actions.

## Стек технологий

Веб-сервер: [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)

Frontend фреймворк: [![React](https://img.shields.io/badge/-React-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)

Backend фреймворк:   [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

API фреймворк: [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

База данных: [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)

## Архитектура приложения 

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.

Контейнер nginx взаимодействует с контейнером backend через gunicorn.

Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

## Документация к проекту

Документация для API после установки доступна по адресу [http://localhost/api/docs/](http://localhost/api/docs/)


## Admin зона

Admin зона django после установки доступна по адресу [http://localhost/admin/](http://localhost/admin/)


## Запуск проекта через Docker

**Для такого запуска на компьютере должно быть приложение Docker!**

1. Клонировать репозиторий и перейти в него в командной строке:

    ```bash
    git clone https://github.com/PavelPolyanskiy/foodgram-st.git
    ```

2. Шаблон наполнения .env можно посмотреть в файле .env.example. Файл с переменными окружения должен лежать в корневой директории.
   
   **Переменную DB_HOST не изменять!**

3. Находясь в папке infra/ поднять контейнеры

    ```bash
    docker compose up -d --build
    ```
4. По адресу [http://localhost](http://localhost) будет доступно веб-приложение


5. Выполнить миграции:

    ```bash
    docker compose exec backend python manage.py migrate
    ```

6. Собрать статику:

    ```bash
    docker compose exec backend python manage.py collectstatic --no-input
    ```

7. Создать суперпользователя (для доступа в Admin-зону Django):

    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```

7. Наполнить базу данных ингредиентами:

    ```bash
    docker compose exec backend python manage.py import_ingredients
    ```

   И также очистить от ингредиентов:
    ```bash
    docker compose exec backend python manage.py clear_ingredients
    ```

8. Заполнить базу данных тегами (завтрак, обед и тд.):

    ```bash
    docker compose exec backend python manage.py import_tags
    ```

   И также очистить от тегов:
    ```bash
    docker compose exec backend python manage.py clear_tags
    ```

