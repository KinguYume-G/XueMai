"""
清理重复/半成品的 APU 大学记录，并为真实的 Asia Pacific University (APU)
记录填充一批真实的 campus.UniversityResource 数据（课程方向、食堂、社团/
生活、招生、图书馆与科研设施等）。

数据全部核实自 apu.edu.my 官网（2026-08），来源见每条记录 `extra.source_url`
字段。产品以 APU 为核心，因此本命令目前只覆盖 APU；其余 10 所大学的资源
数据留待后续按需补充（体量小、非爬取，此命令按官网信息手工核实录入）。

注意：Azusa Pacific University (apu.edu, 美国加州) 是另一所同缩写但完全
不同的学校，不要与本命令中的 apu.edu.my（马来西亚）数据混淆。

运行：
    python manage.py seed_apu_resources
    python manage.py seed_apu_resources --skip-cleanup
"""

from django.core.management.base import BaseCommand

from apps.campus.models import University, UniversityResource

APU_SLUG = "asia-pacific-university"
# The leftover duplicate/junk University row: no website, 0 students, empty
# description, mangled-encoding country — created by an earlier QA/seed pass
# and superseded by the real "asia-pacific-university" row.
DUPLICATE_APU_SLUG = "asia-pacific-university-of-technology-innovation-apu"

SOURCE = "https://www.apu.edu.my"

RESOURCES = [
    {
        "category": "course",
        "title": "Computing & Technology programmes",
        "content": (
            "BSc (Hons) Information Technology (Cloud Engineering / IoT / "
            "FinTech / Cybersecurity specialisms), BSc (Hons) Software "
            "Engineering, BSc (Hons) Computer Science (Quantum Computing / "
            "Data Analytics / AI / Cyber Security specialisms), BA (Hons) "
            "Interactive Media and Immersive Technology, BA (Hons) Game "
            "Development. Postgraduate: MSc Software Engineering, MSc "
            "Artificial Intelligence, MSc Cyber Security, MSc Data Science "
            "and Business Analytics, PhD in Computing/Technology."
        ),
        "source_url": f"{SOURCE}/study-area/computing-technology",
    },
    {
        "category": "course",
        "title": "Engineering programmes",
        "content": (
            "Bachelor of Electrical and Electronic Engineering (Hons), "
            "Bachelor of Mechatronic Engineering (Hons), Bachelor of "
            "Mechanical Engineering (Hons), Bachelor of Petroleum "
            "Engineering (Hons), Bachelor of Computer Engineering (Hons). "
            "All BEM-accredited with Washington Accord recognition; "
            "internships compulsory. Postgraduate: MPhil/PhD in Engineering."
        ),
        "source_url": f"{SOURCE}/study-area/engineering",
    },
    {
        "category": "course",
        "title": "Business & Management programmes",
        "content": (
            "BA (Hons) Business Management, BA (Hons) Human Resource "
            "Management, BA (Hons) International Business Management, BA "
            "(Hons) Digital Marketing. Postgraduate: MBA (multiple "
            "specialisms), Master in Digital Communication, MSc Digital "
            "Marketing, Master of Project Management, PhD in Management, DBA."
        ),
        "source_url": f"{SOURCE}/study-area/business-management",
    },
    {
        "category": "course",
        "title": "Accounting & Finance programmes",
        "content": (
            "Bachelor of Accounting and Finance (Hons) — with Forensic "
            "Accounting / Forex and Investments / Accounting Technology "
            "specialisms — and BSc (Hons) Actuarial Studies — with Data "
            "Analytics / Financial Technology specialisms. Accredited by "
            "ACCA, CIMA and CPA. Postgraduate: Master of Accounting, Master "
            "of Finance (incl. FinTech), PhD in Finance."
        ),
        "source_url": f"{SOURCE}/study-area/accounting-finance",
    },
    {
        "category": "course",
        "title": "Design & Creative Media programmes",
        "content": (
            "BA (Hons) Industrial Design, BA (Hons) Visual Effects, BA "
            "(Hons) Animation, BA (Hons) Digital Advertising. Postgraduate: "
            "Master of Arts in Design Innovation Management (standard and "
            "ODL formats)."
        ),
        "source_url": f"{SOURCE}/study-area/design-creative-media",
    },
    {
        "category": "canteen",
        "title": "Campus dining & cafeteria",
        "content": (
            "APU's cafeteria offers multiple dining options on campus, "
            "alongside a convenience store. The campus sits within "
            "Technology Park Malaysia, Bukit Jalil, with further food "
            "options nearby."
        ),
        "source_url": f"{SOURCE}/campus-facilities",
    },
    {
        "category": "club",
        "title": "Sports, recreation & student life",
        "content": (
            "APU is next to the Bukit Jalil National Sports Complex, "
            "giving students access to world-class facilities for "
            "swimming, football, hockey, squash and more. On campus: a "
            "gymnasium, sports courts, and an indoor social/recreation "
            "space for table tennis, football, pool, chess and other "
            "board games. Student accommodation blocks also include their "
            "own recreational facilities."
        ),
        "source_url": f"{SOURCE}/campus-facilities",
    },
    {
        "category": "event",
        "title": "Application intakes & enrolment",
        "content": (
            "APU runs multiple intake periods per year. International "
            "applicants must have a passport valid for at least 24 months "
            "from the intake date, with academic certificates certified as "
            "true copies. Applications should clearly state the programme "
            "and intake date; results are typically returned within 2-3 "
            "working days of receiving complete documents, followed by a "
            "pre-arrival application processing fee to confirm enrolment "
            "and begin the Student Visa application."
        ),
        "source_url": f"{SOURCE}/international-students-application-procedures",
    },
    {
        "category": "notice",
        "title": "Library & digital learning resources",
        "content": (
            "The APU library provides books, journals, periodicals, "
            "student projects and research materials, plus online digital "
            "library access via providers including ACM, ProQuest, Athens, "
            "Emerald, and Current Law Journals."
        ),
        "source_url": f"{SOURCE}/campus-facilities",
    },
    {
        "category": "notice",
        "title": "Innovation & research facilities",
        "content": (
            "Specialised facilities include the APU CyberSecurity Talent "
            "Zone, an NVIDIA-powered APU AI Supercomputing Lab, the APU "
            "Financial Trading Centre, APU Psychology Centre, APU Games "
            "Lab & Studio, APU XR Studio, APU Green Screen Studio & Media "
            "Hub, Architecture Studio, Robotics Lab, Industrial Design "
            "workshops, and a Google Center of Excellence."
        ),
        "source_url": f"{SOURCE}/campus-facilities",
    },
]


class Command(BaseCommand):
    help = "清理重复的 APU 大学记录并填充真实的 APU UniversityResource 数据"

    def add_arguments(self, parser):
        parser.add_argument("--skip-cleanup", action="store_true", help="跳过清理重复大学记录")

    def handle(self, *args, **options):
        if not options["skip_cleanup"]:
            dup = University.objects.filter(slug=DUPLICATE_APU_SLUG).first()
            if dup and not dup.website and dup.students_count == 0:
                dup.delete()
                self.stdout.write(self.style.WARNING(f"Deleted duplicate/empty University row: {dup}"))

        try:
            university = University.objects.get(slug=APU_SLUG)
        except University.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"University with slug={APU_SLUG!r} not found — run this after the base "
                    "university seed data exists."
                )
            )
            return

        created = 0
        for item in RESOURCES:
            _, was_created = UniversityResource.objects.get_or_create(
                university=university,
                category=item["category"],
                title=item["title"],
                defaults={
                    "content": item["content"],
                    "extra": {"source_url": item["source_url"]},
                    "is_active": True,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} new UniversityResource row(s) for {university.name}."
            )
        )
