import tempfile

from cities_light.models import City, Country
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from PIL import Image

from sensecity_africa.photos.models import Photo, Tag

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoTest(TestCase):
    def _create_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            image = Image.new("RGB", (200, 200), "white")
            image.save(f, "JPEG")
        return open(f.name, mode="rb")

    def setUp(self):
        # select a country and a city
        self.country = Country(name="foo")
        self.country.save()
        self.city = City(name="bar", country=self.country)
        self.city.save()

    def test_photo(self):
        # test the creation of an image
        photo = Photo()
        photo.image = SimpleUploadedFile(
            name="test-image.jpg",
            content=self._create_image().read(),
            content_type="image/jpeg",
        )
        photo.city = self.city
        photo.country = self.country
        photo.save()
        # approve the photo
        photo.moderated_object.approve()
        self.assertEqual(Photo.objects.count(), 1)

        # test that the author is by default blank
        self.assertEqual(photo.author, "")

        # test that we can also have a non-blank author
        photo.author = "martibosch"
        photo.save()
        self.assertNotEqual(photo.author, "")

        # test that we can have zero tags
        self.assertEqual(photo.tags.count(), 0)

        # test that we can add tags
        tags = ["foo", "bar"]
        # we need to create the tag objects and approve them
        for tag_name in tags:
            tag = Tag(name=tag_name)
            tag.save()
            tag.moderated_object.approve()
        photo.tags.add(*tags)
        self.assertEqual(photo.tags.count(), len(tags))

        # test that we cannot create a photo without a city or a country
        new_photo = Photo()
        new_photo.image = SimpleUploadedFile(
            name="test-image.jpg",
            content=self._create_image().read(),
            content_type="image/jpeg",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                new_photo.save()
        new_photo.city = self.city
        # we have a city but we still need a country
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                new_photo.save()
        new_photo.country = self.country
        # now we're good (note that there will be 2 photos at this point)
        new_photo.save()
        return new_photo
        # approve the photo
        new_photo.moderated_object.approve()
        self.assertEqual(Photo.objects.count(), 2)
