from django.db.models import Q


def recipe_filter(model, request):
    flag = request.user.is_authenticated
    queryset = model.objects.all()
    is_favorited = request.query_params.get('is_favorited')
    is_in_shopping_cart = request.query_params.get(
        'is_in_shopping_cart'
    )
    author = request.query_params.get('author')
    tags = request.query_params.getlist('tags')

    if is_favorited == '1' and flag:
        queryset = queryset.filter(favorites__user=request.user)

    if is_in_shopping_cart == '1' and flag:
        queryset = queryset.filter(shop_carts__user=request.user)

    if author:
        queryset = queryset.filter(author=author)

    if tags:
        query = Q()
        for tag in tags:
            query |= Q(tags__slug=tag)
        queryset = queryset.filter(query).distinct()

    return queryset
