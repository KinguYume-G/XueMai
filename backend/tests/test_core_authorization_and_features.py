from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai import views_workflow
from apps.ai.workflows.workflow_engine import WorkflowEngine, WorkflowStatus
from apps.bookmarks.models import Bookmark
from apps.campus.models import University
from apps.comments.models import Comment
from apps.communities.models import Community
from apps.forums.models import Faculty, Forum, Topic
from apps.opportunities.models import ExchangeProgram, Internship, Startup
from apps.posts.models import Bookmark as PostBookmark
from apps.posts.models import Post, PostLike, Tag
from apps.social.models import ChatGroup, ChatMessage, FriendRequest, GroupMember
from apps.users.models import Profile, User


class ObjectAuthorizationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="password123"
        )
        self.attacker = User.objects.create_user(
            username="attacker", email="attacker@example.com", password="password123"
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            is_staff=True,
        )
        self.university = University.objects.create(
            name="Permission University", country="MY", city="Kuala Lumpur"
        )
        self.post = Post.objects.create(
            author=self.owner,
            title="Owner post",
            body="Owner body",
            visibility="public",
            is_published=True,
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.owner, content="Owner comment"
        )
        self.forum = Forum.objects.create(name="Permission Forum")
        self.topic = Topic.objects.create(
            forum=self.forum,
            author=self.owner,
            title="Owner topic",
            content="Owner topic content",
        )
        self.community = Community.objects.create(
            name="Owner Community",
            slug="owner-community",
            description="Owner community description",
            created_by=self.owner,
        )
        future = timezone.now().date() + timedelta(days=30)
        self.exchange = ExchangeProgram.objects.create(
            title="Owner Exchange",
            description="Owner exchange description",
            host_university=self.university,
            location="Kuala Lumpur",
            deadline=future,
            posted_by=self.owner,
        )
        self.internship = Internship.objects.create(
            title="Owner Internship",
            company="Owner Company",
            description="Owner internship description",
            location="Kuala Lumpur",
            type="internship",
            deadline=future,
            posted_by=self.owner,
        )
        self.startup = Startup.objects.create(
            title="Owner Startup",
            org_name="Owner Org",
            description="Owner startup description",
            city="Kuala Lumpur",
            posted_by=self.owner,
        )

    def resources(self):
        return [
            (
                "user",
                f"/api/users/{self.owner.pk}/",
                {"bio": "updated bio"},
                User,
                self.owner.pk,
                "bio",
            ),
            (
                "profile",
                f"/api/profiles/{self.owner.profile.pk}/",
                {"bio": "updated profile"},
                Profile,
                self.owner.profile.pk,
                "bio",
            ),
            (
                "post",
                f"/api/posts/{self.post.pk}/",
                {"title": "updated post"},
                Post,
                self.post.pk,
                "title",
            ),
            (
                "comment",
                f"/api/comments/{self.comment.pk}/",
                {"content": "updated comment"},
                Comment,
                self.comment.pk,
                "content",
            ),
            (
                "topic",
                f"/api/topics/{self.topic.pk}/",
                {"content": "updated topic"},
                Topic,
                self.topic.pk,
                "content",
            ),
            (
                "community",
                f"/api/communities/{self.community.slug}/",
                {"description": "updated community"},
                Community,
                self.community.pk,
                "description",
            ),
            (
                "exchange",
                f"/api/exchange_programs/{self.exchange.pk}/",
                {"description": "updated exchange"},
                ExchangeProgram,
                self.exchange.pk,
                "description",
            ),
            (
                "internship",
                f"/api/internships/{self.internship.pk}/",
                {"description": "updated internship"},
                Internship,
                self.internship.pk,
                "description",
            ),
            (
                "startup",
                f"/api/startups/{self.startup.pk}/",
                {"description": "updated startup"},
                Startup,
                self.startup.pk,
                "description",
            ),
        ]

    def test_non_owners_cannot_update_objects(self):
        self.client.force_authenticate(self.attacker)
        for name, url, payload, model, pk, field in self.resources():
            with self.subTest(resource=name):
                before = getattr(model.objects.get(pk=pk), field)
                response = self.client.patch(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(getattr(model.objects.get(pk=pk), field), before)

    def test_non_owners_cannot_delete_objects(self):
        self.client.force_authenticate(self.attacker)
        for name, url, _payload, model, pk, _field in self.resources():
            with self.subTest(resource=name):
                response = self.client.delete(url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertTrue(model.objects.filter(pk=pk).exists())

    def test_owners_can_update_their_objects(self):
        self.client.force_authenticate(self.owner)
        for name, url, payload, model, pk, field in self.resources():
            with self.subTest(resource=name):
                response = self.client.patch(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                self.assertEqual(getattr(model.objects.get(pk=pk), field), next(iter(payload.values())))

    def test_staff_can_update_objects(self):
        self.client.force_authenticate(self.staff)
        for name, url, payload, model, pk, field in self.resources():
            with self.subTest(resource=name):
                response = self.client.patch(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                self.assertEqual(getattr(model.objects.get(pk=pk), field), next(iter(payload.values())))

    def deletion_resources(self):
        resources = self.resources()
        order = ["comment", "topic", "community", "exchange", "internship", "startup", "post", "profile", "user"]
        by_name = {resource[0]: resource for resource in resources}
        return [by_name[name] for name in order]

    def _assert_actor_can_delete_all_objects(self, actor):
        self.client.force_authenticate(actor)
        for name, url, _payload, model, pk, _field in self.deletion_resources():
            with self.subTest(resource=name):
                response = self.client.delete(url)
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
                self.assertFalse(model.objects.filter(pk=pk).exists())

    def test_owners_can_delete_their_objects(self):
        self._assert_actor_can_delete_all_objects(self.owner)

    def test_staff_can_delete_objects(self):
        self._assert_actor_can_delete_all_objects(self.staff)

    def test_community_create_sets_authenticated_creator(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/communities/",
            {"name": "New Community", "slug": "new-community", "category": "interest"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Community.objects.get(slug="new-community").created_by, self.owner)


class BookmarkFeatureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bookmark-user", password="password123")
        self.owner = User.objects.create_user(username="opportunity-owner", password="password123")
        self.university = University.objects.create(
            name="Bookmark University", country="MY", city="Kuala Lumpur"
        )
        future = timezone.now().date() + timedelta(days=30)
        self.exchange = ExchangeProgram.objects.create(
            title="Bookmark Exchange",
            description="Description",
            host_university=self.university,
            location="Kuala Lumpur",
            deadline=future,
            posted_by=self.owner,
        )
        self.internship = Internship.objects.create(
            title="Bookmark Internship",
            company="Company",
            description="Description",
            location="Kuala Lumpur",
            type="internship",
            deadline=future,
            posted_by=self.owner,
        )
        self.client.force_authenticate(self.user)

    def test_exchange_bookmark_toggle_and_serializer_state(self):
        url = f"/api/exchange_programs/{self.exchange.pk}/bookmark/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["bookmarked"])
        self.assertTrue(
            Bookmark.objects.filter(
                user=self.user, content_type="exchange", object_id=self.exchange.pk
            ).exists()
        )
        detail = self.client.get(f"/api/exchange_programs/{self.exchange.pk}/")
        self.assertTrue(detail.data["bookmarked"])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["bookmarked"])
        self.assertFalse(
            Bookmark.objects.filter(
                user=self.user, content_type="exchange", object_id=self.exchange.pk
            ).exists()
        )

    def test_internship_bookmark_toggle_and_serializer_state(self):
        url = f"/api/internships/{self.internship.pk}/bookmark/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["bookmarked"])
        detail = self.client.get(f"/api/internships/{self.internship.pk}/")
        self.assertTrue(detail.data["bookmarked"])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["bookmarked"])

    def test_generic_bookmark_rejects_dangling_target(self):
        response = self.client.post(
            "/api/bookmarks/",
            {"content_type": "exchange", "object_id": 999999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_generic_bookmark_create_is_idempotent(self):
        payload = {"content_type": "internship", "object_id": self.internship.pk}
        first = self.client.post("/api/bookmarks/", payload, format="json")
        second = self.client.post("/api/bookmarks/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(Bookmark.objects.count(), 1)


class ResourceVisibilityTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="visibility-owner", password="password123")
        self.other = User.objects.create_user(username="visibility-other", password="password123")
        self.staff = User.objects.create_user(
            username="visibility-staff", password="password123", is_staff=True
        )
        self.university = University.objects.create(
            name="Visibility University", country="MY", city="Kuala Lumpur"
        )
        self.forum = Forum.objects.create(name="Visibility Forum")
        self.future = timezone.now().date() + timedelta(days=30)
        self.resources = self._create_resources()

    def _community(self, suffix, owner, **kwargs):
        return Community.objects.create(
            name=f"Community {suffix}",
            slug=f"community-{suffix}",
            created_by=owner,
            **kwargs,
        )

    def _topic(self, suffix, owner, **kwargs):
        return Topic.objects.create(
            forum=self.forum,
            author=owner,
            title=f"Topic {suffix}",
            content="Content",
            **kwargs,
        )

    def _exchange(self, suffix, owner, **kwargs):
        return ExchangeProgram.objects.create(
            title=f"Exchange {suffix}",
            description="Description",
            host_university=self.university,
            location="Kuala Lumpur",
            deadline=self.future,
            posted_by=owner,
            **kwargs,
        )

    def _internship(self, suffix, owner, **kwargs):
        return Internship.objects.create(
            title=f"Internship {suffix}",
            company="Company",
            description="Description",
            location="Kuala Lumpur",
            type="internship",
            deadline=self.future,
            posted_by=owner,
            **kwargs,
        )

    def _startup(self, suffix, owner, **kwargs):
        return Startup.objects.create(
            title=f"Startup {suffix}",
            org_name="Org",
            description="Description",
            city="Kuala Lumpur",
            posted_by=owner,
            **kwargs,
        )

    def _create_resources(self):
        factories = [
            ("/api/communities/", self._community, lambda obj: obj.slug),
            ("/api/topics/", self._topic, lambda obj: obj.pk),
            ("/api/exchange_programs/", self._exchange, lambda obj: obj.pk),
            ("/api/internships/", self._internship, lambda obj: obj.pk),
            ("/api/startups/", self._startup, lambda obj: obj.pk),
        ]
        resources = []
        for url, factory, lookup in factories:
            public = factory("public", self.other)
            own_private = factory("owner-private", self.owner, visibility="private")
            own_draft = factory("owner-draft", self.owner, is_published=False)
            other_private = factory("other-private", self.other, visibility="private")
            resources.append(
                {
                    "url": url,
                    "lookup": lookup,
                    "public": public,
                    "own_private": own_private,
                    "own_draft": own_draft,
                    "other_private": other_private,
                }
            )
        return resources

    @staticmethod
    def _ids(response):
        payload = response.data
        if isinstance(payload, dict):
            payload = payload.get("results", payload.get("data", payload))
        return {item["id"] for item in payload}

    @staticmethod
    def _detail_url(resource, obj):
        return f"{resource['url']}{resource['lookup'](obj)}/"

    def test_anonymous_only_sees_public_published_in_lists_and_details(self):
        for resource in self.resources:
            with self.subTest(url=resource["url"]):
                response = self.client.get(resource["url"])
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(self._ids(response), {resource["public"].pk})
                self.assertEqual(
                    self.client.get(
                        self._detail_url(resource, resource["public"])
                    ).status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    self.client.get(
                        self._detail_url(resource, resource["own_private"])
                    ).status_code,
                    status.HTTP_404_NOT_FOUND,
                )

    def test_authenticated_users_see_public_and_owned_private_or_draft(self):
        self.client.force_authenticate(self.owner)
        for resource in self.resources:
            with self.subTest(url=resource["url"]):
                response = self.client.get(resource["url"])
                self.assertEqual(
                    self._ids(response),
                    {
                        resource["public"].pk,
                        resource["own_private"].pk,
                        resource["own_draft"].pk,
                    },
                )
                self.assertEqual(
                    self.client.get(
                        self._detail_url(resource, resource["own_private"])
                    ).status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    self.client.get(
                        self._detail_url(resource, resource["other_private"])
                    ).status_code,
                    status.HTTP_404_NOT_FOUND,
                )

    def test_staff_can_list_and_retrieve_all_records(self):
        self.client.force_authenticate(self.staff)
        for resource in self.resources:
            with self.subTest(url=resource["url"]):
                response = self.client.get(resource["url"])
                self.assertEqual(
                    self._ids(response),
                    {
                        resource["public"].pk,
                        resource["own_private"].pk,
                        resource["own_draft"].pk,
                        resource["other_private"].pk,
                    },
                )
                self.assertEqual(
                    self.client.get(
                        self._detail_url(resource, resource["other_private"])
                    ).status_code,
                    status.HTTP_200_OK,
                )


class PostReactionIdempotencyTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="post-owner", password="password123")
        self.user = User.objects.create_user(username="post-reactor", password="password123")
        self.post = Post.objects.create(
            author=self.owner,
            title="Public post",
            body="Body",
            visibility="public",
            is_published=True,
        )
        self.client.force_authenticate(self.user)

    def test_like_and_unlike_are_idempotent_and_never_negative(self):
        like_url = f"/api/posts/{self.post.pk}/like/"
        unlike_url = f"/api/posts/{self.post.pk}/unlike/"
        first = self.client.post(like_url)
        retry = self.client.post(like_url)
        self.post.refresh_from_db()
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(retry.status_code, status.HTTP_200_OK)
        self.assertEqual(PostLike.objects.filter(user=self.user, post=self.post).count(), 1)
        self.assertEqual(self.post.likes_count, 1)

        first_remove = self.client.post(unlike_url)
        retry_remove = self.client.post(unlike_url)
        self.post.refresh_from_db()
        self.assertEqual(first_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(retry_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(PostLike.objects.filter(user=self.user, post=self.post).count(), 0)
        self.assertEqual(self.post.likes_count, 0)

    def test_bookmark_and_unbookmark_are_idempotent_and_never_negative(self):
        bookmark_url = f"/api/posts/{self.post.pk}/bookmark/"
        unbookmark_url = f"/api/posts/{self.post.pk}/unbookmark/"
        self.client.post(bookmark_url)
        self.client.post(bookmark_url)
        self.post.refresh_from_db()
        self.assertEqual(
            PostBookmark.objects.filter(user=self.user, post=self.post).count(), 1
        )
        self.assertEqual(self.post.bookmarks_count, 1)

        self.client.post(unbookmark_url)
        retry_remove = self.client.post(unbookmark_url)
        self.post.refresh_from_db()
        self.assertEqual(retry_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(
            PostBookmark.objects.filter(user=self.user, post=self.post).count(), 0
        )
        self.assertEqual(self.post.bookmarks_count, 0)


class SocialAuthorizationTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="group-owner", password="password123")
        self.member = User.objects.create_user(username="group-member", password="password123")
        self.outsider = User.objects.create_user(username="group-outsider", password="password123")
        self.group = ChatGroup.objects.create(name="Private group", creator=self.creator)
        GroupMember.objects.create(group=self.group, user=self.creator, role="owner")
        GroupMember.objects.create(group=self.group, user=self.member)
        self.message = ChatMessage.objects.create(
            from_user=self.creator, group=self.group, content="Private message"
        )

    def test_non_member_cannot_read_send_or_mark_group_messages(self):
        self.client.force_authenticate(self.outsider)
        read = self.client.get(f"/api/chat/messages/?group_id={self.group.pk}")
        send = self.client.post(
            "/api/chat/messages/send/",
            {"group_id": self.group.pk, "content": "Intrusion"},
            format="json",
        )
        mark = self.client.post(
            "/api/chat/messages/mark-read/",
            {"group_id": self.group.pk},
            format="json",
        )
        self.assertEqual(read.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(send.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(mark.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ChatMessage.objects.filter(content="Intrusion").exists())
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_read)

    def test_member_can_read_and_send_but_group_mark_read_does_not_mutate_global_state(self):
        self.client.force_authenticate(self.member)
        read = self.client.get(f"/api/chat/messages/?group_id={self.group.pk}")
        send = self.client.post(
            "/api/chat/messages/send/",
            {"group_id": self.group.pk, "content": "Member message"},
            format="json",
        )
        mark = self.client.post(
            "/api/chat/messages/mark-read/",
            {"group_id": self.group.pk},
            format="json",
        )
        self.assertEqual(read.status_code, status.HTTP_200_OK)
        self.assertEqual(send.status_code, status.HTTP_201_CREATED)
        self.assertEqual(mark.status_code, status.HTTP_200_OK)
        self.assertEqual(mark.data["data"]["marked_count"], 0)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_read)

    def test_friend_request_rejects_self_same_direction_and_reverse_duplicates(self):
        self.client.force_authenticate(self.member)
        self_request = self.client.post(
            "/api/chat/friend-request/", {"to_user_id": self.member.pk}, format="json"
        )
        first = self.client.post(
            "/api/chat/friend-request/", {"to_user_id": self.outsider.pk}, format="json"
        )
        duplicate = self.client.post(
            "/api/chat/friend-request/", {"to_user_id": self.outsider.pk}, format="json"
        )
        self.client.force_authenticate(self.outsider)
        reverse = self.client.post(
            "/api/chat/friend-request/", {"to_user_id": self.member.pk}, format="json"
        )
        self.assertEqual(self_request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(reverse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendRequest.objects.count(), 1)


class ForumStatisticsTests(APITestCase):
    def setUp(self):
        # DRF throttles use a process-level cache that otherwise leaks request
        # counts from earlier API test cases into these anonymous endpoint tests.
        cache.clear()

    def test_statistics_handle_empty_database(self):
        overview = self.client.get("/api/forums/overview/")
        self.assertEqual(overview.status_code, status.HTTP_200_OK)
        self.assertEqual(
            overview.data,
            {"faculty_count": 0, "major_count": 0, "active_posts": 0, "active_users": 0},
        )
        hot = self.client.get("/api/topics/hot/")
        self.assertEqual(hot.status_code, status.HTTP_200_OK)
        self.assertEqual(hot.data, [])

    def test_statistics_are_aggregated_from_real_records(self):
        Faculty.objects.create(name="Computing", slug="computing", major_count=4)
        Faculty.objects.create(name="Business", slug="business", major_count=3)
        forum = Forum.objects.create(name="Statistics Forum")
        user_a = User.objects.create_user(username="stats-a", password="password123")
        user_b = User.objects.create_user(username="stats-b", password="password123")
        tag_a = Tag.objects.create(name="AI")
        tag_b = Tag.objects.create(name="Careers")
        topic_a = Topic.objects.create(
            forum=forum, author=user_a, title="A", content="A content"
        )
        topic_b = Topic.objects.create(
            forum=forum, author=user_b, title="B", content="B content"
        )
        topic_a.tags.add(tag_a, tag_b)
        topic_b.tags.add(tag_a)

        overview = self.client.get("/api/forums/overview/")
        self.assertEqual(
            overview.data,
            {"faculty_count": 2, "major_count": 7, "active_posts": 2, "active_users": 2},
        )
        hot = self.client.get("/api/topics/hot/?window=7d&limit=2")
        self.assertEqual(hot.status_code, status.HTTP_200_OK)
        self.assertEqual(hot.data[0], {"name": "AI", "post_count": 2})
        self.assertEqual(hot.data[1], {"name": "Careers", "post_count": 1})


class WorkflowAuthorizationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="workflow-owner", password="password123")
        self.other = User.objects.create_user(username="workflow-other", password="password123")
        self.staff = User.objects.create_user(
            username="workflow-staff", password="password123", is_staff=True
        )
        self.engine = WorkflowEngine(ai_executor=lambda *_args, **_kwargs: "ok")
        self.context = self.engine.create_workflow(
            workflow_id="owned-workflow",
            user=self.owner,
            initial_input="test",
            steps=[],
        )
        self.context.status = WorkflowStatus.FAILED
        self.context.error = "internal provider secret and path"
        self.previous_engine = views_workflow._workflow_engine
        views_workflow._workflow_engine = self.engine

    def tearDown(self):
        views_workflow._workflow_engine = self.previous_engine

    def test_workflow_status_is_owner_scoped(self):
        self.client.force_authenticate(self.other)
        response = self.client.get("/api/ai/workflow/status/owned-workflow/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.owner)
        response = self.client.get("/api/ai/workflow/status/owned-workflow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["error"], "Workflow execution failed")
        self.assertNotIn("provider secret", str(response.data))

        self.client.force_authenticate(self.staff)
        response = self.client.get("/api/ai/workflow/status/owned-workflow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streaming_errors_are_sanitized(self):
        class FailingEngine:
            def create_workflow(self, **kwargs):
                return SimpleNamespace(**kwargs)

            def execute_workflow(self, *_args, **_kwargs):
                raise RuntimeError("private provider details")

        self.client.force_authenticate(self.owner)
        with patch("apps.ai.views_workflow.get_workflow_engine", return_value=FailingEngine()):
            response = self.client.post(
                "/api/ai/workflow/execute/",
                {
                    "input": "test",
                    "custom_steps": [
                        {
                            "id": "one",
                            "name": "One",
                            "function_id": "general_chat",
                            "description": "Test",
                        }
                    ],
                },
                format="json",
            )
            body = b"".join(response.streaming_content).decode("utf-8")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Workflow execution failed", body)
        self.assertNotIn("private provider details", body)
