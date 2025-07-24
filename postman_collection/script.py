import requests
from backend.recipe.models import Tag

url = 'http://127.0.0.1:8000/api/v1/users/'  # замените на ваш URL

# for i in range(3, 9):
#     data = {
#     "email": f"test{i}@text.ru", "username": f"test{i}", "first_name": f"test{i}", "last_name": f"test{i}", "password": f"test{i}"
#     }
#     headers = {
#     'Content-Type': 'application/json',
#     # если нужно, добавьте авторизацию, например:
#     # 'Authorization': 'Bearer YOUR_TOKEN',
#     }
#     response = requests.post(url, json=data, headers=headers)
#     print('Статус ответа:', response.status_code)
#     print('Тело ответа:', response.text)

tags = Tag.objects.create(name='breakfest', slug='breakfest')
tags = Tag.objects.create(name='dinner', slug='dinner')