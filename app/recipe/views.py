"""
Views for Recipes API
"""
from rest_framework import (
    viewsets,
    mixins,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
)

from recipe import serializers

""" Viewset is setup to work with Model """


class RecipeViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    """ Override queryset method """

    def get_queryset(self):
        """ Retrieve recipes for authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            """ return ONLY reference not to class NOT instantiated () """
            return serializers.RecipeSerializer

        """ returns RecipeDetailSerializer """
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create new recipe """

        """ Add current auth user to user """
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ Manage tags in the database """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter return queryset for only authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')
