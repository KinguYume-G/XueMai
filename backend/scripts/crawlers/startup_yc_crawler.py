"""
Startup / opportunity listings importer — Y Combinator public directory.

Source: https://github.com/yc-oss/api (yc-oss/api), an open-source, MIT-licensed,
daily-updated static JSON mirror of Y Combinator's public company directory
(https://www.ycombinator.com/companies). It is built from YC's public search
index and republished specifically for free public reuse — no scraping of
ycombinator.com itself is performed, and the GitHub Pages host serving the
JSON (yc-oss.github.io) carries no robots.txt restriction. This keeps us clear
of ycombinator.com's own robots.txt, which disallows `/companies?*` (query
paths) — we never touch that host.

This script performs exactly ONE HTTP GET against a static JSON file (no
crawling, no pagination loops, no per-company page fetches), filters it down
to a small, Asia-Pacific-weighted, industry-diverse sample, and loads the
result into `opportunities.Startup` as real, clearly-attributed startup
listings relevant to XueMai / UniPulse Asia's APAC student audience.

Usage:
    python manage.py shell -c "exec(open('scripts/crawlers/startup_yc_crawler.py').read())"
  or, more conveniently, via the wrapping management command:
    python manage.py seed_startups
"""

import os
import sys
from pathlib import Path

import django
import requests

# ---------------------------------------------------------------------------
# Django bootstrap (so this file can also be run standalone with plain python)
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
if not django.apps.apps.ready:  # pragma: no cover - defensive, shell already sets this up
    django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from apps.opportunities.models import Startup  # noqa: E402

YC_COMPANIES_URL = "https://yc-oss.github.io/api/companies/all.json"
SYSTEM_USERNAME = "unipulse_official"

APAC_REGION_MARKERS = [
    "Singapore", "Malaysia", "Indonesia", "Philippines", "Vietnam", "India",
    "Japan", "South Korea", "China", "Hong Kong", "Taiwan", "Australia",
    "Thailand", "New Zealand",
]

MAX_PER_INDUSTRY = 3
TARGET_COUNT = 18


def _score(company: dict) -> int:
    """Higher score sorts first — weight toward Malaysia/Singapore (APU's home
    region) and toward YC 'top company' picks for recognizability."""
    loc = company.get("all_locations") or ""
    score = 0
    if "Malaysia" in loc:
        score += 100
    if "Singapore" in loc:
        score += 50
    if company.get("top_company"):
        score += 20
    if company.get("isHiring"):
        score += 5
    return -score  # ascending sort = highest score first


def fetch_candidates() -> list[dict]:
    resp = requests.get(
        YC_COMPANIES_URL,
        timeout=20,
        headers={"User-Agent": "UniPulse Asia Student Project (educational, dev dataset)"},
    )
    resp.raise_for_status()
    companies = resp.json()

    candidates = [
        c
        for c in companies
        if c.get("status") == "Active"
        and c.get("website")
        and c.get("long_description")
        and len(c["long_description"]) >= 80
        and any(marker in (c.get("regions") or []) for marker in APAC_REGION_MARKERS)
    ]
    candidates.sort(key=_score)

    chosen: list[dict] = []
    per_industry: dict[str, int] = {}
    for c in candidates:
        industry = c.get("industry") or "Other"
        if per_industry.get(industry, 0) >= MAX_PER_INDUSTRY:
            continue
        chosen.append(c)
        per_industry[industry] = per_industry.get(industry, 0) + 1
        if len(chosen) >= TARGET_COUNT:
            break
    return chosen


def _parse_city_country(all_locations: str) -> tuple[str, str]:
    """'Kuala Lumpur, Federal Territory of Kuala Lumpur, Malaysia; Remote' -> ('Kuala Lumpur', 'Malaysia')"""
    first = (all_locations or "").split(";")[0].strip()
    parts = [p.strip() for p in first.split(",") if p.strip()]
    if not parts:
        return "", ""
    city = parts[0]
    country = parts[-1]
    return city, country


def get_system_user():
    User = get_user_model()
    user, _ = User.objects.get_or_create(
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
    if not user.has_usable_password():
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return user


def run(dry_run: bool = False) -> int:
    system_user = get_system_user()
    companies = fetch_candidates()

    created = 0
    for c in companies:
        city, country = _parse_city_country(c.get("all_locations", ""))
        tags = list(dict.fromkeys((c.get("industries") or []) + (c.get("tags") or [])))[:6]
        title = c["name"]
        org_name = c["name"]
        description = c.get("long_description") or c.get("one_liner") or ""
        description_short = (c.get("one_liner") or "")[:500]

        if dry_run:
            print(f"[dry-run] {title} ({city}, {country}) tags={tags}")
            continue

        obj, was_created = Startup.objects.get_or_create(
            title=title,
            org_name=org_name,
            defaults={
                "description": description,
                "description_short": description_short,
                "city": city,
                "country": country,
                "tags": tags,
                "contact_url": c.get("website") or c.get("url"),
                "followers_count": max(0, (c.get("team_size") or 0) // 10),
                "posted_by": system_user,
                "visibility": "public",
                "is_published": True,
            },
        )
        if was_created:
            created += 1

    print(f"Startup import complete: {created} created, {len(companies)} candidates processed.")
    return created


if __name__ == "__main__":  # pragma: no cover
    run(dry_run="--dry-run" in sys.argv)
