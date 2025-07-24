from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (UserViewSet, TagViewSet, IngredientViewSet,
                       RecipeViewSet, SubscribtionsViewSet)

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
    path(
        'users/subscriptions/',
        SubscribtionsViewSet.as_view({'get': 'list'})
    ),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
