from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from api.views import (IngredientsViewSet, RecipeViewSet, TagsViewSet,
                       UserViewSet)

router = SimpleRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='api-docs',
    ),
]
