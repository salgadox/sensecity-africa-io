from cities_light.models import City, Country
from django.db import models
from django.utils.translation import gettext_lazy as _
from location_field.models.spatial import LocationField
from moderation.db import ModeratedModel
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase
from versatileimagefield.fields import VersatileImageField

from .managers import _TaggableManager


class Tag(TagBase, ModeratedModel):
    # other metadata only useful for backend purposes
    is_public = models.BooleanField(default=False)

    # for moderation
    class Moderator:
        notify_user = False
        visibility_column = "is_public"


class TaggedPhoto(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class Photo(ModeratedModel):
    MIN_TAGS = 1
    MAX_TAGS = 4
    DEFAULT_ZOOM = 7

    image = VersatileImageField(_("Image"), upload_to="images/")
    author = models.CharField(max_length=255, blank=True, verbose_name=_("Author"))
    tags = TaggableManager(through=TaggedPhoto, blank=True, manager=_TaggableManager)

    # location
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, verbose_name=_("Country")
    )
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name=_("City"))
    location = LocationField(
        verbose_name=_("Location"),
        based_fields=["city"],
        blank=True,
        null=True,
        zoom=DEFAULT_ZOOM,
    )

    # other metadata only useful for backend purposes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    # for moderation
    class Moderator:
        notify_user = False
        visibility_column = "is_public"
