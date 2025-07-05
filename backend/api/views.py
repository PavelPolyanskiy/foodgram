from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated



from .serializers import (UserMeSerializer, UserSignUpSerializer,
                          AvatarSerializer, PasswordSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeCreateSerializer, FollowSerializer,
                          RecipeReadSerializer)
from recipe.models import Tag, Ingredient, Recipe

User = get_user_model()

# Create your views here.



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny, )  # pomenyai /////////// dssssssssssssssssssssss
    #lookup_field = 'username'
    #http_method_names = ['get', 'post', 'patch', 'delete']
    #filter_backends = [filters.SearchFilter]
    #search_fields = ['username']
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['retrieve', 'me']:
            return UserMeSerializer
        if self.action == 'set_password':
            return PasswordSerializer


    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, ),
        serializer_class=UserMeSerializer
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(detail=False,
            methods=['put', 'delete'],
            permission_classes=(IsAuthenticated, ),
            url_path='me/avatar/',
            serializer_class=AvatarSerializer
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user = request.user
            user.avatar = settings.DEFAULT_AVATAR
            user.save()
            return Response(status.HTTP_204_NO_CONTENT)
        
    @action(detail=False,
            methods=['post'],
            permission_classes=(IsAuthenticated, ),
            url_path='set_password',
            serializer_class=PasswordSerializer
    )
    def set_password(self, request):
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if user.check_password(serializer.validated_data['current_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                'Пароль успешно изменен',
                status.HTTP_204_NO_CONTENT
            )
        return Response('Пароли не совпадают', status.HTTP_404_NOT_FOUND)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get', 'post') # Потом убери!                           вава


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    http_method_names = ('get', 'post') # Потом убери!                           вава


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post') # Потом убери!                           вава
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # search_fields = ['slug']
    # pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeReadSerializer


class FollowViewSet(viewsets.GenericViewSet,
                    CreateModelMixin, ListModelMixin):
    """Вьюсет для модели Follow."""

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username',) ############################ ne nugno vrode

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)