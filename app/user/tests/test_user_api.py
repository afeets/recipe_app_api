"""
Tests for User API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')

""" Helper Function """


def create_user(**params):
    """ Create return new user """
    return get_user_model().objects.create_user(**params)


""" Public Tests - don't require authentication """


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """ Test creating user is successful """
        payload = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'name': 'Test User'
        }

        """ POST request, sending payload """
        res = self.client.post(CREATE_USER_URL, payload)

        """ Assertions """
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        """ Retrieve new user from DB """
        user = get_user_model().objects.get(email=payload['email'])

        """ Assert password is correct """
        self.assertTrue(user.check_password(payload['password']))

        """ Make sure password is not returned in data response - SECURITY!!!"""
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """ Test error returned if user with email exists """
        payload = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'name': 'Test User'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test error is returned if password less than 5 chars """
        payload = {
            'email': 'test@example.com',
            'password': 'Pass',  # Password to short
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        """ Confirm user does not exist in DB """
        self.assertFalse(user_exists)
