from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.campus.models import University
from apps.communities.models import Community
from apps.opportunities.models import ExchangeProgram
from apps.posts.models import Post


class GlobalSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="alice", email="alice@example.com", password="password-123"
        )
        self.university = University.objects.create(
            name="Asia Pacific University", country="Malaysia", city="Kuala Lumpur"
        )
        Post.objects.create(author=self.user, body="Python study group", visibility="public")
        Post.objects.create(author=self.user, body="private Python notes", visibility="private")
        Community.objects.create(
            name="Python Club",
            slug="python-club",
            description="Learn Python together",
            created_by=self.user,
        )
        Community.objects.create(
            name="Private Python Club",
            slug="private-python-club",
            description="Hidden group",
            created_by=self.user,
            visibility="private",
        )
        ExchangeProgram.objects.create(
            title="Python Research Exchange",
            description="Research exchange",
            host_university=self.university,
            location="Kuala Lumpur",
            deadline=date.today() + timedelta(days=30),
            posted_by=self.user,
            visibility="public",
        )

    def test_rejects_too_short_query(self):
        response = self.client.get("/api/search/", {"q": "P"})
        self.assertEqual(response.status_code, 400)

    def test_returns_grouped_public_results(self):
        response = self.client.get("/api/search/", {"q": "Python"})
        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        self.assertEqual(len(payload["results"]["posts"]), 1)
        self.assertEqual(len(payload["results"]["communities"]), 1)
        self.assertEqual(payload["results"]["communities"][0]["slug"], "python-club")
        self.assertEqual(payload["results"]["opportunities"][0]["kind"], "exchange")
