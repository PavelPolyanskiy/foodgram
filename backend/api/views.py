from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import (UserSerializer, UserCreateSerializer,
                          AvatarSerializer, PasswordSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, FollowSerializer,
                          RecipeReadSerializer, FavoriteSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer)
from recipe.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Follow
from .utils import ShoppingCartDownloader
from .filters import recipe_filter
from .permissions import AuthorOrReadOnly
from .paginators import RecipePagination

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    #pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['me', 'list']:
            return UserSerializer
        return UserCreateSerializer

    #     return UserSignUpSerializer

    # @action(
    #     detail=False,
    #     methods=['get'],
    #     permission_classes=(IsAuthenticated, ),
    #     serializer_class=UserSerializer
    # )
    # def me(self, request):
    #     user = request.user
    #     if request.method == 'GET':
    #         serializer = self.get_serializer(user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

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

    # @action(detail=False,
    #         methods=['post'],
    #         permission_classes=(IsAuthenticated, ),
    #         url_path='set_password',
    #         serializer_class=PasswordSerializer
    #         )
    # def set_password(self, request):
    #     user = request.user

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = request.user
    #     if user.check_password(
    #         serializer.validated_data.get('current_password')
    #     ):
    #         user.set_password(serializer.validated_data.get('new_password'))
    #         user.save()
    #         return Response(
    #             'Пароль успешно изменен.',
    #             status=status.HTTP_204_NO_CONTENT
    #         )

    #     return Response('Текущий пароль неверный.', status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
        url_path='subscribe',
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        data = {'following': author.id}

        if request.method == 'POST':
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
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscribtionsViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ('get',)
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = LimitOffsetPagination
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
                status=status.HTTP_400_BAD_REQUEST
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
                {'detail': 'Рецепт не найден в корзине покупок'},
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
        recipe = Recipe.objects.get(id=pk)
        if recipe:
            scheme, host = request.scheme, request.get_host()
            link = recipe.short_link.short_link
            url = f'{scheme}://{host}/recipes/s/{link}'
            return Response({'url': url}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
