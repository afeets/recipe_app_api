"""
Views for Recipes API
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        """ returns RecipeDetailSerializer """
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create new recipe """

        """ Add current auth user to user """
        serializer.save(user=self.request.user)

    """
    Custom Action, detail means to a specific recipe id,
    if False this would be for a list viewset
    """
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """ Base viewset for Recipe Attributes """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter return queryset for only authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """ Manage tags in the database """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Manage ingredients in the database """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
