from django.conf import settings
from django.db import router
from taggit.managers import _TaggableManager as _TaggitTaggableManager


class _TaggableManager(_TaggitTaggableManager):
    def _to_tag_model_instances(self, tags, tag_kwargs):
        """
        Takes an iterable containing either strings, tag objects, or a mixture
        of both and returns set of tag objects.
        """
        db = router.db_for_write(self.through, instance=self.instance)

        str_tags = set()
        tag_objs = set()

        for t in tags:
            if isinstance(t, self.through.tag_model()):
                tag_objs.add(t)
            elif isinstance(t, str):
                str_tags.add(t)
            else:
                raise ValueError(
                    "Cannot add"
                    f" {t} ({type(t)}). Expected {type(self.through.tag_model())} or"
                    " str."
                )

        case_insensitive = getattr(settings, "TAGGIT_CASE_INSENSITIVE", False)
        manager = self.through.tag_model()._default_unmoderated_manager.using(db)

        if case_insensitive:
            # Some databases can do case-insensitive comparison with IN, which
            # would be faster, but we can't rely on it or easily detect it.
            existing = []
            tags_to_create = []

            for name in str_tags:
                try:
                    tag = manager.get(name__iexact=name)
                    existing.append(tag)
                except self.through.tag_model().DoesNotExist:
                    tags_to_create.append(name)
        else:
            # If str_tags has 0 elements Django actually optimizes that to not
            # do a query.  Malcolm is very smart.
            existing = manager.filter(name__in=str_tags, **tag_kwargs)

            tags_to_create = str_tags - {t.name for t in existing}

        tag_objs.update(existing)

        for new_tag in tags_to_create:
            if case_insensitive:
                lookup = {"name__iexact": new_tag, **tag_kwargs}
            else:
                lookup = {"name": new_tag, **tag_kwargs}

            tag, create = manager.get_or_create(**lookup, defaults={"name": new_tag})
            tag_objs.add(tag)

        return tag_objs
