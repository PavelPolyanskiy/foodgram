from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6


class RecipeLimitPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
