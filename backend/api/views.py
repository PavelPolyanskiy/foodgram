from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


from recipe.models import (Favorite, Ingredient, Recipe,
                           ShoppingCart, Tag)
from users.models import Follow
from .filters import RecipeFilter, IngredientFilter
from .paginators import FoodgramPagination
from .permissions import AuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeReadSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer, ShoppingCartSerializer)

from .utils import ShoppingCartDownloader

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    pagination_class = FoodgramPagination
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=(IsAuthenticated, ),
        url_path='me/avatar',
        serializer_class=AvatarSerializer
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated, ),
        url_path='subscribe',
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        data = {'following': author.id}

        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, id=None):
        deleted, _ = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, pk=id)
        ).delete()

        if not deleted:
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, ),
        url_path='subscriptions',
        pagination_class=FoodgramPagination
    )
    def subscriptions(self, request, id=None):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = FoodgramPagination
    permission_classes = (AuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateUpdateSerializer

        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated, ),
        url_path='favorite',
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        data = {'user': request.user.id, 'recipe': recipe.id}
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        deleted, _ = Favorite.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()

        if not deleted:
            return Response(
                {'detail': 'Рецепт не найден в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        data = {'user': request.user.id, 'recipe': recipe.id}
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        deleted, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()

        if not deleted:
            return Response(
                {'detail': 'Рецепт не найден в корзине покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        return ShoppingCartDownloader.download_shopping_list(request)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(AllowAny, ),
        url_path='get-link',
    )
    def short_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        short_code = recipe.short_link
        scheme, host = request.scheme, request.get_host()
        url = f'{scheme}://{host}/s/{short_code}'
        return Response({'short-link': url}, status=status.HTTP_200_OK)


def short_link_view_redirect(request, short_code):
    recipe = get_object_or_404(Recipe, short_link=short_code)

    return HttpResponseRedirect(
        request.build_absolute_uri(f'/recipes/{recipe.id}/')
    )
