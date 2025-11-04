from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from unidecode import unidecode
from apps.posts.models import Tag


class Command(BaseCommand):
    help = "Backfill/repair Tag.slug values"

    @transaction.atomic
    def handle(self, *args, **options):
        fixed = 0
        for tag in Tag.objects.all().order_by("id"):
            base = slugify(unidecode((tag.name or "").strip())) or "tag"
            candidate = base
            i = 2
            while Tag.objects.filter(slug=candidate).exclude(pk=tag.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            if not tag.slug or tag.slug != candidate:
                tag.slug = candidate
                tag.save(update_fields=["slug"])
                fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed} tag(s)."))
