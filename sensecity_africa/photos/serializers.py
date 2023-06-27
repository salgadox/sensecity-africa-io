from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from .models import Photo


class PhotoSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    country = serializers.ReadOnlyField(source="country.name")
    city = serializers.ReadOnlyField(source="city.name")

    class Meta:
        model = Photo
        fields = ["image", "author", "tags", "country", "city", "location"]
