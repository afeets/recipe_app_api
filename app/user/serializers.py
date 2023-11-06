""""
Serializers for the User API View
Used to convert to and from Python objects
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
  """ Serializer for user object """

  """ Tell django model and fields args to pass """
  class Meta:
    model = get_user_model()
    fields = ['email','password','name']
    extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

  def create(self, validated_data):
    """ Create and return a user with encrypted password """
    return get_user_model().objects.create_user(**validated_data)