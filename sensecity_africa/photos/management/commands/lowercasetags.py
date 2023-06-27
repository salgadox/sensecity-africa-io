from django.core.management.base import BaseCommand

from sensecity_africa.photos.models import Tag


class Command(BaseCommand):
    # See http://yuguangzhang.com/blog/merge-tags-with-django-taggit/
    args = "none"
    help = "all tag names"

    def handle(self, *args, **options):
        tags = Tag.objects.all()
        count = tags.count()
        for i, tag in enumerate(tags):
            if i % 20 == 0:
                self.stdout.write("Lowercasing %d/%d\n" % (i + 1, count))
            tag.name = tag.name.lower()
            tag.save()
