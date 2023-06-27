from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from sensecity_africa.photos.models import Tag, TaggedPhoto


class Command(BaseCommand):
    # See http://yuguangzhang.com/blog/merge-tags-with-django-taggit/
    help = "merges all tags automatically"

    def merge(self, extra_slugs, dest_slug):
        try:
            dest_tag = Tag.objects.get(slug=dest_slug)
        except ObjectDoesNotExist:
            raise CommandError("Destination Tag '%s' does not exist" % dest_slug)

        for slug in extra_slugs:
            try:
                tag = Tag.objects.get(slug=slug)
            except ObjectDoesNotExist:
                raise CommandError("Tag '%s' does not exist" % slug)

            items = TaggedPhoto.objects.filter(tag=tag)
            count = items.count()
            for i, item in enumerate(items):
                if i % 20 == 0:
                    self.stdout.write("Merging %s %d/%d\n" % (slug, i + 1, count))
                obj = item.content_object
                if not obj:
                    return
                obj.tags.remove(tag)
                obj.tags.add(dest_tag)
            tag.delete()

            self.stdout.write("Successfully merged tags into '%s'\n" % dest_slug)

    def handle(self, *args, **options):
        for tag in Tag.objects.all():
            tags = Tag.objects.filter(name__iexact=tag.name.lower())
            if tags.count() > 1:
                tags = tags.order_by("id")
                dest = tags[0].slug
                extras = []
                for extra_tag in tags[1::]:
                    extras.append(extra_tag.slug)
                self.merge(extras, dest)
