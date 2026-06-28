
def filter_recipes(queryset, request):
    author = request.query_params.get('author')
    if author:
        try:
            queryset = queryset.filter(author_id=int(author))
        except (ValueError, TypeError):
            return queryset.none()

    tags = request.query_params.getlist('tags')
    if tags:
        queryset = queryset.filter(tags__slug__in=tags).distinct()

    is_favorited = request.query_params.get('is_favorited')
    if is_favorited == '1' and request.user.is_authenticated:
        queryset = queryset.filter(favorited_by__user=request.user)

    is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
    if is_in_shopping_cart == '1' and request.user.is_authenticated:
        queryset = queryset.filter(in_shopping_cart__user=request.user)

    return queryset
