from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.opportunities.models import ExchangeProgram

User = get_user_model()


class Command(BaseCommand):
    help = "填充交换项目测试数据"

    def handle(self, *args, **options):
        self.stdout.write("开始填充交换项目数据...")

        # 获取或创建一个管理员用户作为发布者
        try:
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                admin_user = User.objects.first()

            if not admin_user:
                self.stdout.write(self.style.ERROR("错误：没有找到用户，请先创建超级用户"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"获取用户失败: {e}"))
            return

        # 清空现有数据
        deleted_count = ExchangeProgram.objects.all().delete()[0]
        self.stdout.write(f"已删除 {deleted_count} 个现有项目")

        # 创建测试数据
        programs_data = [
            {
                "title": "2025春季交换项目",
                "country": "SG",
                "location": "新加坡",
                "deadline": date(2025, 12, 31),
                "description": "亚洲顶尖大学交换项目，提供丰富的学术资源和国际化环境。",
                "tuition": "S$15,000/学期",
                "gpa_min": "3.5",
                "lang_req": "雅思≥7.0",
                "rating_avg": 4.8,
                "rating_count": 234,
                "applied_count": 567,
                "cover_url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800",
                "website": "https://nus.edu.sg",
                "is_urgent": True,
                "requirements": "GPA≥3.5, 雅思≥7.0",
                "posted_by": admin_user,
                "host_university": None,  # 暂时为空，稍后处理
            },
            {
                "title": "2025暑期研究项目",
                "country": "HK",
                "location": "香港",
                "deadline": date(2025, 11, 20),
                "description": "为期两个月的高端学术研究项目，与顶尖教授合作进行前沿研究。",
                "tuition": "HK$25,000/项目",
                "gpa_min": "3.3",
                "lang_req": "托福≥90",
                "rating_avg": 4.6,
                "rating_count": 189,
                "applied_count": 423,
                "cover_url": "https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=800",
                "website": "https://hku.hk",
                "is_urgent": True,
                "requirements": "GPA≥3.3, 托福≥90",
                "posted_by": admin_user,
                "host_university": None,
            },
            {
                "title": "2026秋季交换项目",
                "country": "JP",
                "location": "东京",
                "deadline": date(2026, 3, 15),
                "description": "体验日本顶尖大学的学术氛围，深入了解日本文化与科技发展。",
                "tuition": "¥800,000/学期",
                "gpa_min": "3.2",
                "lang_req": "日语N2",
                "rating_avg": 4.7,
                "rating_count": 156,
                "applied_count": 389,
                "cover_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800",
                "website": "https://u-tokyo.ac.jp",
                "is_urgent": False,
                "requirements": "GPA≥3.2, 日语N2",
                "posted_by": admin_user,
                "host_university": None,
            },
            {
                "title": "2026年度交换项目",
                "country": "AU",
                "location": "墨尔本",
                "deadline": date(2026, 1, 30),
                "description": "南半球顶尖大学，提供优质的教育资源和多元文化体验。",
                "tuition": "AU$20,000/学期",
                "gpa_min": "3.0",
                "lang_req": "雅思≥6.5",
                "rating_avg": 4.5,
                "rating_count": 203,
                "applied_count": 512,
                "cover_url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800",
                "website": "https://unimelb.edu.au",
                "is_urgent": False,
                "requirements": "GPA≥3.0, 雅思≥6.5",
                "posted_by": admin_user,
                "host_university": None,
            },
        ]

        # 尝试获取或创建大学
        university_names = {
            "SG": "新加坡国立大学",
            "HK": "香港大学",
            "JP": "东京大学",
            "AU": "墨尔本大学",
        }

        created_programs = []
        for data in programs_data:
            try:
                # 尝试导入并获取大学
                try:
                    from apps.campus.models import University

                    university, _ = University.objects.get_or_create(
                        name=university_names[data["country"]],
                        defaults={
                            "name": university_names[data["country"]],
                            "country": data["country"],
                            "city": data["location"],
                        },
                    )
                    data["host_university"] = university
                except ImportError:
                    # 如果没有 campus 应用，跳过外键
                    self.stdout.write(
                        self.style.WARNING("警告：campus 应用不存在，跳过 host_university")
                    )
                    # host_university 可能不允许为空，需要处理
                    pass

                # 创建项目（如果 host_university 是必需的且为空，这里会失败）
                program = ExchangeProgram.objects.create(**data)
                created_programs.append(program)
                self.stdout.write(
                    self.style.SUCCESS(f"[OK] Created: {program.title} ({program.country})")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[ERROR] Failed to create {data["title"]}: {e}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"\n=== Successfully created {len(created_programs)} exchange programs ==="
            )
        )
        self.stdout.write(f"Total count: {ExchangeProgram.objects.count()}")
