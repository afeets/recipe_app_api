"""
Serializers for recipe APIs
"""

from rest_framework import serializers
from core.models import (
    Recipe,
    Tag
)


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tags """

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipes """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """ Handle getting or creating tags as needed """

        """ get authenticated user """
        auth_user = self.context['request'].user

        """ loop add or find tags (don't add duplicates), with auth user """
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """ Overwrite default method to allow adding of tags """

        """ remove tags from object and assign to variable """
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Update Recipe """
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for recipe detail view """

    """ Import RecipeSerializer Class"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
