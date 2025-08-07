from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class RecipeLimitPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'


class UserPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
