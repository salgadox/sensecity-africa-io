import tempfile

from cities_light.models import City, Country
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from PIL import Image

from sensecity_africa.photos.models import Photo

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoTest(TestCase):
    def _create_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            image = Image.new("RGB", (200, 200), "white")
            image.save(f, "JPEG")
        return open(f.name, mode="rb")

    def setUp(self):
        self.image = self._create_image()

        # create a country and a city
        self.country = Country(name="foo")
        self.country.save()
        self.city = City(name="bar", country=self.country)
        self.city.save()

    def tearDown(self):
        self.image.close()

    def test_photo(self):
        # test the creation of an image
        photo = Photo()
        photo.image = SimpleUploadedFile(
            name="test-image.jpg",
            content=self.image.read(),
            content_type="image/jpeg",
        )
        photo.city = self.city
        photo.country = self.country
        photo.save()
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
        photo.tags.add(*tags)
        self.assertEqual(photo.tags.count(), len(tags))

        # test that we cannot create a photo without a city or a country
        new_photo = Photo()
        new_photo.image = SimpleUploadedFile(
            name="test-image.jpg",
            content=self.image.read(),
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
        self.assertEqual(Photo.objects.count(), 2)
