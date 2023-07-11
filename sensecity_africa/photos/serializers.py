from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField
from versatileimagefield.serializers import VersatileImageFieldSerializer

from .models import Photo


class PhotoSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    country = serializers.ReadOnlyField(source="country.name")
    city = serializers.ReadOnlyField(source="city.name")

    class Meta:
        model = Photo
        fields = ["image", "author", "tags", "country", "city", "location"]


class PhotoUploadSerializer(TaggitSerializer, serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(sizes=[("full_size", "url")])
    tags = TagListSerializerField()

    class Meta:
        model = Photo
        fields = ["image", "author", "tags", "country", "city", "location"]
