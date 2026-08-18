"""Cross-module search API."""

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.communities.models import Community
from apps.forums.models import Topic
from apps.opportunities.models import ExchangeProgram, Internship, Startup
from apps.posts.models import Post
from apps.users.models import User
from core.permissions import filter_public_or_owned


def _requested_types(raw_type: str) -> set[str]:
    allowed = {"users", "posts", "topics", "communities", "opportunities"}
    if not raw_type or raw_type == "all":
        return allowed
    requested = {item.strip() for item in raw_type.split(",") if item.strip()}
    return requested & allowed


@api_view(["GET"])
@permission_classes([AllowAny])
def global_search(request):
    query = request.query_params.get("q", "").strip()
    if len(query) < 2:
        return Response(
            {
                "data": None,
                "error": {"code": "invalid_query", "message": "搜索关键词至少需要 2 个字符"},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        limit = min(max(int(request.query_params.get("limit", 6)), 1), 20)
    except (TypeError, ValueError):
        limit = 6
    types = _requested_types(request.query_params.get("type", "all"))

    results: dict[str, list[dict]] = {}

    if "users" in types:
        users = (
            User.objects.filter(is_active=True)
            .filter(Q(username__icontains=query) | Q(profile__major__icontains=query))
            .select_related("profile", "profile__university")[:limit]
        )
        results["users"] = [
            {
                "id": user.id,
                "username": user.username,
                "avatar_url": str(user.avatar) if user.avatar else user.profile.avatar_url,
                "major": getattr(user.profile, "major", ""),
                "university": (
                    user.profile.university.name
                    if getattr(user, "profile", None) and user.profile.university
                    else ""
                ),
            }
            for user in users
        ]

    if "posts" in types:
        posts = (
            Post.objects.visible_to(request.user)
            .filter(Q(title__icontains=query) | Q(body__icontains=query), is_published=True)
            .select_related("author")
            .order_by("-created_at")[:limit]
        )
        results["posts"] = [
            {
                "id": post.id,
                "title": post.title or post.body[:80],
                "excerpt": post.body[:180],
                "author": post.author.username,
                "created_at": post.created_at.isoformat(),
            }
            for post in posts
        ]

    if "topics" in types:
        topics = (
            filter_public_or_owned(Topic.objects.all(), request.user, "author")
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .select_related("author", "forum")
            .order_by("-updated_at")[:limit]
        )
        results["topics"] = [
            {
                "id": topic.id,
                "title": topic.title,
                "excerpt": topic.content[:180],
                "forum_id": topic.forum_id,
                "author": topic.author.username,
            }
            for topic in topics
        ]

    if "communities" in types:
        communities = (
            filter_public_or_owned(Community.objects.all(), request.user, "created_by")
            .filter(Q(name__icontains=query) | Q(description__icontains=query))
            .order_by("-members")[:limit]
        )
        results["communities"] = [
            {
                "id": community.id,
                "slug": community.slug,
                "name": community.name,
                "description": community.description[:180],
                "members": community.members,
            }
            for community in communities
        ]

    if "opportunities" in types:
        opportunity_results: list[dict] = []
        exchanges = ExchangeProgram.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query),
            is_published=True,
            visibility="public",
        ).order_by("deadline")[:limit]
        opportunity_results.extend(
            {
                "id": item.id,
                "kind": "exchange",
                "title": item.title,
                "subtitle": item.location,
            }
            for item in exchanges
        )

        remaining = max(0, limit - len(opportunity_results))
        internships = Internship.objects.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(description__icontains=query),
            is_published=True,
            visibility="public",
        ).order_by("-created_at")[:remaining]
        opportunity_results.extend(
            {
                "id": item.id,
                "kind": "internship",
                "title": item.title,
                "subtitle": item.company,
            }
            for item in internships
        )

        remaining = max(0, limit - len(opportunity_results))
        startups = (
            filter_public_or_owned(Startup.objects.all(), request.user, "posted_by")
            .filter(
                Q(title__icontains=query)
                | Q(org_name__icontains=query)
                | Q(description__icontains=query)
            )
            .order_by("-created_at")[:remaining]
        )
        opportunity_results.extend(
            {
                "id": item.id,
                "kind": "startup",
                "title": item.title,
                "subtitle": item.org_name,
            }
            for item in startups
        )
        results["opportunities"] = opportunity_results

    return Response(
        {
            "data": {
                "query": query,
                "results": results,
                "total": sum(len(items) for items in results.values()),
            },
            "error": None,
        }
    )
