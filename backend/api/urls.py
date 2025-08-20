from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet,
                       TagViewSet, UserViewSet)

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

    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),

]
