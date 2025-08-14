from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet, ShortLinkView,
                       SubscriptionsAPIView, TagViewSet, UserViewSet,
                       short_link_view_redirect)

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
        SubscriptionsAPIView.as_view(),
        name='subscriptions'
    ),
    path('recipes/<int:pk>/get-link/', ShortLinkView.as_view()),
    path(
        'recipes/s/<str:short_code>',
        short_link_view_redirect,
        name='short_link_redirect'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),

]
