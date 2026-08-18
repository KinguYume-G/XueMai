"""
清理早期 QA/冒烟测试遗留的 Faculty / Forum / Topic / Community 垃圾数据，
并基于 Asia Pacific University (APU, apu.edu.my) 官方网站信息填充真实的
学院（Faculty）、论坛（Forum）与少量系统账号发布的入门话题（Topic）。

数据来源（均为 2026-08 通过 apu.edu.my 官网核实，非编造）：
  - https://www.apu.edu.my/study-area/computing-technology
  - https://www.apu.edu.my/study-area/engineering
  - https://www.apu.edu.my/study-area/business-management
  - https://www.apu.edu.my/study-area/accounting-finance
  - https://www.apu.edu.my/study-area/design-creative-media
  - https://www.apu.edu.my/campus-facilities
注意：Azusa Pacific University (apu.edu, 美国加州) 是另一所同缩写但完全
不同的学校，本命令中的数据均核实自 apu.edu.my（马来西亚，本产品对应的
真实 APU），未与 Azusa Pacific 数据混淆。

话题内容由平台官方系统账号 `unipulse_official` 发布（欢迎/专业介绍类
内容，非真实用户发帖，也不是抓取自任何真人在其他平台发布的内容），
避免冒充任何真实用户或误标作者。

运行：
    python manage.py seed_apu_forums
    python manage.py seed_apu_forums --skip-cleanup
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.forums.models import Faculty, Forum, Topic

User = get_user_model()

SYSTEM_USERNAME = "unipulse_official"

# Faculty/Forum/Topic content, verified against apu.edu.my (see module docstring).
FACULTIES = [
    {
        "name": "Computing & Technology",
        "description": (
            "APU's oldest and most established school. Covers IT, Software "
            "Engineering, Computer Science, Interactive Media & Immersive "
            "Technology, and Game Development, from foundation through PhD."
        ),
        "major_count": 5,
        "welcome_topic": {
            "title": "Welcome to Computing & Technology — programmes at a glance",
            "content": (
                "A quick, factual rundown of what APU's Computing & Technology "
                "study area actually offers, so new students and prospective "
                "applicants have one place to start:\n\n"
                "- BSc (Hons) Information Technology — specialisms in Cloud "
                "Engineering, IoT, FinTech, Cybersecurity\n"
                "- BSc (Hons) Software Engineering\n"
                "- BSc (Hons) Computer Science — specialisms in Quantum "
                "Computing, Data Analytics, AI, Cyber Security\n"
                "- BA (Hons) Interactive Media and Immersive Technology\n"
                "- BA (Hons) Game Development\n"
                "- Postgraduate: MSc Software Engineering, MSc Artificial "
                "Intelligence, MSc Cyber Security, MSc Data Science and "
                "Business Analytics, PhD in Computing / PhD in Technology\n\n"
                "Source: apu.edu.my/study-area/computing-technology. Ask "
                "programme-specific questions in this forum and fellow "
                "students/alumni can chime in."
            ),
            "tags": ["APU", "Computing", "编程"],
        },
    },
    {
        "name": "Engineering",
        "description": (
            "Programmes accredited by the Board of Engineers Malaysia (BEM) "
            "with Washington Accord recognition, spanning electrical, "
            "mechanical, mechatronic, petroleum and computer engineering."
        ),
        "major_count": 5,
        "welcome_topic": {
            "title": "Welcome to Engineering — programmes at a glance",
            "content": (
                "What APU's Engineering study area covers:\n\n"
                "- Bachelor of Electrical and Electronic Engineering (Hons)\n"
                "- Bachelor of Mechatronic Engineering (Hons)\n"
                "- Bachelor of Mechanical Engineering (Hons)\n"
                "- Bachelor of Petroleum Engineering (Hons)\n"
                "- Bachelor of Computer Engineering (Hons)\n"
                "- Postgraduate: MPhil in Engineering, PhD in Engineering\n\n"
                "All undergraduate programmes are BEM-accredited and "
                "internships are compulsory, per BEM requirements. Source: "
                "apu.edu.my/study-area/engineering."
            ),
            "tags": ["APU", "Engineering"],
        },
    },
    {
        "name": "Business & Management",
        "description": (
            "Business Management, HR Management, International Business "
            "Management and Digital Marketing, with MBA and doctoral options."
        ),
        "major_count": 4,
        "welcome_topic": {
            "title": "Welcome to Business & Management — programmes at a glance",
            "content": (
                "What APU's Business & Management study area covers:\n\n"
                "- BA (Hons) Business Management — specialisms in E-Business, "
                "Digital Leadership, AI & Business Analytics, Business "
                "Economics\n"
                "- BA (Hons) Human Resource Management — People Analytics "
                "specialism available\n"
                "- BA (Hons) International Business Management — Supply "
                "Chain Management specialism available\n"
                "- BA (Hons) Digital Marketing\n"
                "- Postgraduate: MBA (multiple specialisms), Master in "
                "Digital Communication, MSc Digital Marketing, Master of "
                "Project Management, MPhil in Management, PhD in "
                "Management, DBA\n\n"
                "Source: apu.edu.my/study-area/business-management."
            ),
            "tags": ["APU", "Business"],
        },
    },
    {
        "name": "Accounting & Finance",
        "description": (
            "Accounting & Finance and Actuarial Studies programmes with "
            "accreditation from ACCA, CIMA and CPA."
        ),
        "major_count": 7,
        "welcome_topic": {
            "title": "Welcome to Accounting & Finance — programmes at a glance",
            "content": (
                "What APU's Accounting & Finance study area covers:\n\n"
                "- Bachelor of Accounting and Finance (Hons) — plus "
                "specialisms in Forensic Accounting, Forex and Investments, "
                "Accounting Technology\n"
                "- BSc (Hons) Actuarial Studies — plus specialisms in Data "
                "Analytics, Financial Technology\n"
                "- Postgraduate: Master of Accounting, Master of Accounting "
                "in Forensic Analysis, Master of Finance (incl. FinTech "
                "specialism), PhD in Finance\n\n"
                "Professional accreditation from ACCA, CIMA and CPA. "
                "Source: apu.edu.my/study-area/accounting-finance."
            ),
            "tags": ["APU", "Finance"],
        },
    },
    {
        "name": "Design & Creative Media",
        "description": (
            "Industrial Design, Visual Effects, Animation and Digital "
            "Advertising, with hands-on studio-based learning."
        ),
        "major_count": 4,
        "welcome_topic": {
            "title": "Welcome to Design & Creative Media — programmes at a glance",
            "content": (
                "What APU's Design & Creative Media study area covers:\n\n"
                "- BA (Hons) Industrial Design\n"
                "- BA (Hons) Visual Effects\n"
                "- BA (Hons) Animation\n"
                "- BA (Hons) Digital Advertising\n"
                "- Postgraduate: Master of Arts in Design Innovation "
                "Management (standard and ODL)\n\n"
                "Source: apu.edu.my/study-area/design-creative-media."
            ),
            "tags": ["APU", "Design"],
        },
    },
]

# A short, generic getting-started topic posted once into each forum.
HOW_TO_USE_TITLE = "How to use this forum"
HOW_TO_USE_CONTENT = (
    "A few quick notes from the UniPulse Asia team:\n\n"
    "- This forum is for questions, discussion and resource-sharing "
    "related to this study area at APU.\n"
    "- Be specific in your topic title — it helps other students find "
    "and answer it.\n"
    "- Mark your topic as solved once you get a good answer, so others "
    "searching later know it's resolved.\n"
    "- Keep posts honest and on-topic; this is a space for real "
    "students helping each other.\n\n"
    "If you spot something wrong or missing, let us know — this "
    "platform is actively improving."
)


class Command(BaseCommand):
    help = "清理 QA junk 数据并填充真实 APU Faculty/Forum/Topic 数据"

    def add_arguments(self, parser):
        parser.add_argument("--skip-cleanup", action="store_true", help="跳过清理 QA junk 数据")

    def handle(self, *args, **options):
        if not options["skip_cleanup"]:
            self._cleanup_junk()

        system_user = self._get_system_user()

        with transaction.atomic():
            for faculty_data in FACULTIES:
                faculty, f_created = Faculty.objects.get_or_create(
                    name=faculty_data["name"],
                    defaults={
                        "description": faculty_data["description"],
                        "major_count": faculty_data["major_count"],
                    },
                )
                if not f_created:
                    faculty.description = faculty_data["description"]
                    faculty.major_count = faculty_data["major_count"]
                    faculty.save(update_fields=["description", "major_count"])

                forum, forum_created = Forum.objects.get_or_create(
                    name=f"{faculty_data['name']} Forum",
                    defaults={
                        "description": faculty_data["description"],
                        "icon": "graduation-cap",
                    },
                )
                if forum_created:
                    self.stdout.write(self.style.SUCCESS(f"Forum created: {forum.name}"))

                welcome = faculty_data["welcome_topic"]
                self._ensure_topic(forum, system_user, welcome["title"], welcome["content"], welcome["tags"])
                self._ensure_topic(
                    forum, system_user, HOW_TO_USE_TITLE, HOW_TO_USE_CONTENT, ["APU", "指南"]
                )

            # Faculty.topic_count is a display-only counter (see model
            # comment) — keep it in sync with what we just created.
            for faculty_data in FACULTIES:
                try:
                    faculty = Faculty.objects.get(name=faculty_data["name"])
                    forum = Forum.objects.get(name=f"{faculty_data['name']} Forum")
                except (Faculty.DoesNotExist, Forum.DoesNotExist):
                    continue
                faculty.topic_count = forum.topics.count()
                faculty.save(update_fields=["topic_count"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Faculties={Faculty.objects.count()} Forums={Forum.objects.count()} "
                f"Topics={Topic.objects.count()}"
            )
        )

    def _cleanup_junk(self):
        junk_topics = Topic.objects.filter(forum__name__icontains="QA Smoke")
        junk_count = junk_topics.count()
        if junk_count:
            junk_topics.delete()
            self.stdout.write(self.style.WARNING(f"Deleted {junk_count} QA junk topic(s)"))

        junk_forums = Forum.objects.filter(name__icontains="QA Smoke")
        forum_count = junk_forums.count()
        if forum_count:
            junk_forums.delete()
            self.stdout.write(self.style.WARNING(f"Deleted {forum_count} QA junk forum(s)"))

    def _get_system_user(self):
        user, created = User.objects.get_or_create(
            username=SYSTEM_USERNAME,
            defaults={
                "email": "official@unipulse.asia",
                "bio": (
                    "UniPulse Asia 官方账号 / Official system account used for "
                    "platform announcements and curated content. Not a real student."
                ),
                "is_staff": True,
            },
        )
        if created and not user.has_usable_password():
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user

    def _ensure_topic(self, forum, author, title, content, tag_names):
        if Topic.objects.filter(forum=forum, title=title).exists():
            return
        from apps.posts.models import Tag

        topic = Topic.objects.create(
            forum=forum,
            author=author,
            title=title,
            content=content,
            visibility="public",
            is_published=True,
        )
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            topic.tags.add(tag)
        self.stdout.write(self.style.SUCCESS(f"  Topic created: {title}"))
