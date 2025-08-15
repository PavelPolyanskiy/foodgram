from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipe.models import (Favorite, Ingredient, Recipe, RecipeShortLink,
                           ShoppingCart, Tag)
from users.models import Follow
from .filters import recipe_filter
from .paginators import RecipeLimitPagination, CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)
from .utils import ShoppingCartDownloader

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.all()
        return super().get_queryset()

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
        methods=['put', 'delete'],
        permission_classes=(IsAuthenticated, ),
        url_path='me/avatar',
        serializer_class=AvatarSerializer
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                instance=user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            user = request.user
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
        url_path='subscribe',
    )
    def subscribe(self, request, *args, **kwargs):
        pk = kwargs.get('pk') or kwargs.get('id')
        user = request.user
        author = get_object_or_404(User, id=pk)
        data = {'following': author.id}

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FollowSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            follow = Follow.objects.filter(user=user.id, following=author.id)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', )
    search_fields = ('name', )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = CustomPagination
    permission_classes = (AuthorOrReadOnly, )

    def get_queryset(self):

        return recipe_filter(Recipe, self.request)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateUpdateSerializer

        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
        pagination_class=RecipeLimitPagination,
        url_path='favorite',
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            serializer = FavoriteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user.id, recipe=recipe.id)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Рецепт не найден в избранном.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            serializer = ShoppingCartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                user=user.id, recipe=recipe.id
            )
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Рецепт не найден в корзине покупок.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        return ShoppingCartDownloader.download_shopping_list(request)


class ShortLinkView(APIView):

    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe:
            if not RecipeShortLink.objects.filter(recipe=recipe).exists():
                RecipeShortLink.objects.create(recipe=recipe)

            scheme, host = request.scheme, request.get_host()
            code = recipe.short_link.short_link
            url = f'{scheme}://{host}/s/{code}'
            return Response({'short-link': url}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


def short_link_view_redirect(request, short_code):
    short_link = get_object_or_404(RecipeShortLink, short_link=short_code)
    return redirect(f'/recipes/{short_link.recipe.id}/')
