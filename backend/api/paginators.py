from rest_framework.pagination import PageNumberPagination


class RecipeLimitPagination(PageNumberPagination):
    limit_query_param = 'recipes_limit'


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
