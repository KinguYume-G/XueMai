"""
清理 QA 测试用创业数据，并从 Y Combinator 公开目录导入一批真实的
Asia-Pacific 相关创业公司作为创业机会（opportunities.Startup）。

数据来源见 backend/scripts/crawlers/startup_yc_crawler.py 顶部注释。

运行：
    python manage.py seed_startups
    python manage.py seed_startups --dry-run   # 仅打印将要导入的公司，不写库
    python manage.py seed_startups --skip-cleanup  # 不清理旧的 QA junk 数据
"""

import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.opportunities.models import Startup

CRAWLERS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "crawlers"


class Command(BaseCommand):
    help = "清理 QA junk 创业数据，并从 Y Combinator 公开目录导入真实创业公司数据"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="只打印将导入的数据，不写库")
        parser.add_argument(
            "--skip-cleanup", action="store_true", help="跳过清理标题包含 'QA Smoke' 的测试数据"
        )

    def handle(self, *args, **options):
        if not options["skip_cleanup"]:
            junk = Startup.objects.filter(title__icontains="QA Smoke")
            junk_count = junk.count()
            if junk_count:
                junk.delete()
                self.stdout.write(self.style.WARNING(f"已清理 {junk_count} 条 QA 测试创业数据"))

        if str(CRAWLERS_DIR) not in sys.path:
            sys.path.insert(0, str(CRAWLERS_DIR))
        import startup_yc_crawler  # noqa: E402  (path-injected import)

        try:
            created = startup_yc_crawler.run(dry_run=options["dry_run"])
        except Exception as exc:  # network failure, YC schema change, etc.
            self.stderr.write(self.style.ERROR(f"导入失败: {exc}"))
            return

        if not options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"新建 {created} 条创业机会数据"))
