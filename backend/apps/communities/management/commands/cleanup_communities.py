"""
清理早期 QA 冒烟测试遗留的 Community 数据，并修复因 slug 生成 bug
（slugify() 在遇到纯中文名称时会直接产出空字符串）而导致 slug 为空/
低质量的历史社区记录。

Community 详情页按 slug 查找（lookup_field = "slug"），slug 为空的社区
在前端完全无法点击进入 —— 是一个真实的死链接 bug，而不只是数据缺失。
Community.save() 已修复为使用 unidecode 音译（见 apps/communities/models.py），
本命令只是把修复应用到已经落库的历史数据上。

运行：
    python manage.py cleanup_communities
    python manage.py cleanup_communities --dry-run
"""

from django.core.management.base import BaseCommand

from apps.communities.models import Community


class Command(BaseCommand):
    help = "清理 QA junk 社区数据，并修复历史上因中文名生成空 slug 的社区"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        junk = Community.objects.filter(name__icontains="QA Smoke") | Community.objects.filter(
            name__icontains="QA Verify"
        )
        junk_count = junk.count()
        if junk_count:
            names = list(junk.values_list("name", flat=True))
            if not dry_run:
                junk.delete()
            self.stdout.write(
                self.style.WARNING(f"{'Would delete' if dry_run else 'Deleted'} {junk_count}: {names}")
            )

        fixed = 0
        for community in Community.objects.all():
            if not community.slug:
                old = community.slug
                if not dry_run:
                    community.slug = ""  # force save() to regenerate via unidecode
                    community.save()
                fixed += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{'Would fix' if dry_run else 'Fixed'} slug for '{community.name}': "
                        f"{old!r} -> {'' if dry_run else community.slug!r}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"Done. {fixed} slug(s) fixed."))
