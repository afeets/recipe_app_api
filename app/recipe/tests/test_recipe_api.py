"""
Tests for Recipe API
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ Create and return recipe detail URL """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """ Helper Function - Create and return sample recipe """
    defaults = {
        'title': 'Sample Recipe Title',
        'time_minutes': 22,
        'price': Decimal('1.00'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf',
    }
    """ Overwrite dictionary with provided params """
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """ Test unauthenticated API Requests """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test Auth is required to call API """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """ Test authenticated API Requests """

    """ setup creates user """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'Password123!'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        """ Make request to API """
        res = self.client.get(RECIPES_URL)

        """ Return by id in reverse order"""
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """ Test list of recipes limited to authenticated user """
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'Password123!',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """ Test get recipe detail """
        recipe = create_recipe(user=self.user)

        """ get url for recipe """
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
