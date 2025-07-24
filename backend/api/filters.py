def recipe_filter(model, request):
    queryset = model.objects.all()
    is_favorited = request.query_params.get('is_favorited')
    is_in_shopping_cart = request.query_params.get(
        'is_in_shopping_cart'
    )
    author = request.query_params.get('author')
    tags = request.query_params.get('tags')
    if is_favorited == '1':
        queryset = queryset.filter(favorites__user=request.user)

    if is_in_shopping_cart == '1':
        queryset = queryset.filter(shop_carts__user=request.user)

    if author:
        queryset = queryset.filter(author=author)

    if tags:
        tags_split = tags.split(',')
        for tag in tags_split:
            queryset = queryset.filter(tags__slug=tag)

    return queryset