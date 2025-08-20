# Проект Foodgram

## Описание 

Данное веб-приложение позволяет читать и делиться рецептами, добавлять понравившиеся в избранное, а также подписываться на авторов рецептов.

Для удобства, есть возможность добавить рецепт(-ы) в корзину и скачать для них список покупок в .txt формате. 
В полученном списке будут все продукты, необходимые для приготовления рецепта(-ов), добавленных в корзину покупок. 
Повторяющиеся ингредиенты суммируются.

У проекта реализованы CI/CD  с помощью GitHub Actions.

## Пример работы проекта

URL: https://paskalfoodgram.ddns.net/

Документация: https://paskalfoodgram.ddns.net/api/docs/

## Запуск проекта, используя Docker 

**Необходимо приложение Docker!**

1. Клонировать репозиторий и перейти в него в командной строке:

    ```bash
    git clone https://github.com/PavelPolyanskiy/foodgram.git
    ```

2. Шаблон наполнения .env можно посмотреть в файле .env.example. Файл с переменными окружения должен лежать в корневой директории.
   
   **Переменную DB_HOST не изменять!**
   
   **Для использования в проекте БД Postgres, необходимо указать в переменной CURRENT_DATABASE=postgres (не чувствительно к регистру).**

3. Перейти в папку foodgram/, поднять контейнеры

    ```bash
    docker compose up -d --build
    ```

4. По адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/) будет доступно веб-приложение


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

8. Заполнить базу данных тегами:

    ```bash
    docker compose exec backend python manage.py import_tags
    ```

## Стек технологий

Веб-сервер: [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)

Frontend фреймворк: [![React](https://img.shields.io/badge/-React-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)

Backend фреймворк:   [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

API фреймворк: [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

База данных: [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)

## Как наполнить БД данными

1. Наполнить базу данных ингредиентами:

    ```bash
    docker compose exec backend python manage.py import_ingredients
    ```

2. Заполнить базу данных тегами:

    ```bash
    docker compose exec backend python manage.py import_tags
    ```


## Архитектура приложения 

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.

Контейнер nginx взаимодействует с контейнером backend через gunicorn.

Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

## Документация к API

Документация для API после установки доступна по адресу [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)


## Пример запросов/ответов

#### Get all recipes

```http
  GET /api/recipes/
```

| Parameter | Type     | Description                                                            |
| :-------- | :------- |:-----------------------------------------------------------------------|
| `page` | `integer` | Номер страницы.                                                        |
| `limit` | `integer` | Количество объектов на странице.                                       |
| `is_favorited` | `integer` | Enum: `0` `1`. Показывать только рецепты, находящиеся в списке избранного. |
| `is_in_shopping_cart` | `integer` | Enum: `0` `1`. Показывать только рецепты, находящиеся в списке покупок. |
| `author` | `integer` | Показывать рецепты только автора с указанным id.                                                        |
| `tags` | `Array of strings` | xample: `tags=lunch&tags=breakfast`. Показывать рецепты только с указанными тегами (по slug)                                            |

<details>
<summary>Response</summary>

```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
</details>

#### Get recipe

```http
  GET /api/recipes/{id}/
```
<details>
<summary>Response</summary>

```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
</details>

| Parameter | Type     | Description                                            |
| :-------- | :------- |:-------------------------------------------------------|
| `id`      | `string` | **Required**. Уникальный идентификатор этого рецепта  |


## Автор проекта
[Полянский Павел](https://github.com/PavelPolyanskiy)
