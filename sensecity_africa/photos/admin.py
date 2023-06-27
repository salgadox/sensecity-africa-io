from django.contrib import admin
from moderation.admin import ModerationAdmin

from .forms import PhotoForm
from .models import Photo, Tag


@admin.register(Photo)
class PhotoAdmin(ModerationAdmin):
    form = PhotoForm


@admin.register(Tag)
class TagAdmin(ModerationAdmin):
    pass
