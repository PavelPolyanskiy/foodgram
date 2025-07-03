from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views 

from api.views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

router_v1 = DefaultRouter()

router_v1.register(
    prefix='users',
    viewset=UserViewSet,
    basename='user'
)

router_v1.register(
    prefix='tags',
    viewset=TagViewSet,
    basename='tag'
)

router_v1.register(
    prefix='ingredients',
    viewset=IngredientViewSet,
    basename='ingredient'
)

router_v1.register(
    prefix='recipes',
    viewset=RecipeViewSet,
    basename='recipe'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('api/v1/auth/token/login/', views.obtain_auth_token) #какой из них рабочий?
    # path('api/v1/auth/', include('djoser.urls.jwt')) # kak eto ispravit' ?????????? наведи здесь красоту
]
