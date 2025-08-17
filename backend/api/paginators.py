from rest_framework.pagination import PageNumberPagination

from .constants import PAGINATION_PAGE_SIZE, PAGE_SIZE_QUERY_PARAM


class RecipeLimitPagination(PageNumberPagination):
    limit_query_param = 'recipes_limit'


class CustomPagination(PageNumberPagination):
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
