from dal import autocomplete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Photo


class PhotoForm(autocomplete.FutureModelForm):
    required_css_class = "required"

    class Meta:
        model = Photo
        fields = ["image", "author", "tags", "country", "city", "location"]
        widgets = {
            "tags": autocomplete.TaggitSelect2(
                url="photos:tag-autocomplete",
                attrs={
                    "data-placeholder": _("List of tags"),
                    "data-minimum-input-length": 2,
                },
            ),
            "country": autocomplete.ModelSelect2(url="photos:country"),
            "city": autocomplete.ModelSelect2(
                url="photos:city",
                forward=["country"],
                attrs={"data-minimum-input-length": 1},
            ),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", [])
        if len(tags) < Photo.MIN_TAGS or len(tags) > Photo.MAX_TAGS:
            raise ValidationError(
                _("The number of tags must be at least %(min)s and at most %(max)s")
                % {"min": Photo.MIN_TAGS, "max": Photo.MAX_TAGS},
                code="invalid",
            )
        return tags
