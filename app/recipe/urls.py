"""
URL Mappings for recipe app
"""
from recipe import views
from rest_framework.routers import DefaultRouter
from django.urls import (
    path,
    include,
)

""" DefaultRouter works with API View to auto create endpoints """

""" auto creates recipe endpoints """
router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
