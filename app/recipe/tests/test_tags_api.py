"""
Tests for recipe API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """ Create and return tag detail url """
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user1@example.com', password='Password123'):
    """ Create and return a User """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """ Test unauthenticated API requests """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required for retrieving tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ Test authenticated API Requests """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving list of tags """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test list of tags is limited to authenticated user """
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruit')
        tag = Tag.objects.create(user=self.user, name='Vegetable')

        """ request, ensure only retrieve 1 tag of user """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ Test updating a tag """
        tag = Tag.objects.create(user=self.user, name='Initial Tag Name')

        payload = {'name': 'New Tag Name'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """ Test deleting a tag """
        tag = Tag.objects.create(user=self.user, name='Tag to delete')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        """ Now confirm no tags exists """
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """ Test listing tags by those assigned to recipes """
        t1 = Tag.objects.create(user=self.user, name='Breakfast')
        t2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.tags.add(t2)

        """ response returns only ingredients assigned to recipes """
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(t1)
        s2 = TagSerializer(t2)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s1.data, res.data)

    def test_filtered_tags_unique(self):
        """ Test filtered tags returns a unique list """
        t1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Scrambled Eggs',
            time_minutes=60,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tags.add(t1)
        recipe2.tags.add(t1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        """
        ensure tag is only listed once despite
        assigned to two recipes
        """
        self.assertEqual(len(res.data), 1)
