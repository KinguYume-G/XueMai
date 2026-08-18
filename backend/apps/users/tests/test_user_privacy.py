"""
User Privacy Protection Tests
确保未认证用户无法访问敏感信息（email, bio）
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserPrivacyTestCase(TestCase):
    """测试用户隐私保护"""

    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()

        # 创建测试用户
        self.user1 = User.objects.create_user(
            username="alice", email="alice@example.com", password="testpass123"
        )
        self.user1.bio = "Alice's bio - should be private"
        self.user1.save()

        self.user2 = User.objects.create_user(
            username="bob", email="bob@example.com", password="testpass123"
        )

    def test_unauthenticated_cannot_see_email(self):
        """未认证用户不能看到 email 字段"""
        response = self.client.get(f"/api/users/{self.user1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ✅ 应该包含公开字段
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("created_at", response.data)

        # ❌ 不应该包含敏感字段
        self.assertNotIn("email", response.data)
        self.assertNotIn("bio", response.data)

        print("✅ 测试通过: 未认证用户无法看到 email/bio")

    def test_authenticated_can_see_email(self):
        """认证用户可以看到 email 字段"""
        # 登录
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(f"/api/users/{self.user1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ✅ 应该包含所有字段
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("bio", response.data)
        self.assertIn("created_at", response.data)

        # 验证实际值
        self.assertEqual(response.data["email"], "alice@example.com")
        self.assertEqual(response.data["bio"], "Alice's bio - should be private")

        print("✅ 测试通过: 认证用户可以看到完整信息")

    def test_unauthenticated_cannot_search_by_email(self):
        """未认证用户不能通过 email 搜索用户"""
        # 尝试搜索 email
        response = self.client.get("/api/users/?search=alice@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 应该返回空结果（email 不在搜索字段中）
        # 或者不返回匹配结果
        results = response.data.get("results", response.data)

        # 如果返回了结果，确保不是通过 email 匹配的
        # 我们期望未认证用户搜索 email 返回空
        if isinstance(results, list):
            email_matches = [r for r in results if "email" in str(r).lower()]
            # 由于 email 不在 search_fields，应该没有匹配
            self.assertEqual(len(results), 0, "未认证用户不应通过 email 搜索到结果")

        print("✅ 测试通过: 未认证用户无法通过 email 搜索")

    def test_authenticated_can_search_by_email(self):
        """认证用户可以通过 email 搜索用户"""
        # 登录
        self.client.force_authenticate(user=self.user2)

        # 通过 email 部分内容搜索
        response = self.client.get("/api/users/?search=alice@")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)
        if isinstance(results, list):
            # 应该找到 alice
            self.assertGreater(len(results), 0, "认证用户应该能通过 email 搜索到结果")

            # 验证找到的是正确的用户
            usernames = [r["username"] for r in results]
            self.assertIn("alice", usernames)

        print("✅ 测试通过: 认证用户可以通过 email 搜索")

    def test_unauthenticated_users_list_privacy(self):
        """测试用户列表接口的隐私保护"""
        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)
        if isinstance(results, list) and len(results) > 0:
            first_user = results[0]

            # 公开字段应该存在
            self.assertIn("username", first_user)

            # 敏感字段不应该存在
            self.assertNotIn("email", first_user)
            self.assertNotIn("bio", first_user)

        print("✅ 测试通过: 用户列表隐私保护正常")

    def test_profile_search_email_protection(self):
        """测试 Profile 搜索的 email 保护"""
        # 未认证用户尝试通过 email 搜索 profile
        response = self.client.get("/api/profiles/?search=alice@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)
        if isinstance(results, list):
            # 应该返回空结果（email 不在未认证用户的搜索字段中）
            self.assertEqual(len(results), 0, "未认证用户不应通过 email 搜索到 profile")

        print("✅ 测试通过: Profile email 搜索保护正常")


class UserSerializerTestCase(TestCase):
    """测试序列化器的正确性"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user.bio = "Test bio"
        self.user.save()

    def test_public_serializer_fields(self):
        """测试公开序列化器只包含安全字段"""
        from apps.users.serializers import UserPublicSerializer

        serializer = UserPublicSerializer(self.user)
        data = serializer.data

        # 应该包含的字段
        self.assertIn("id", data)
        self.assertIn("username", data)
        self.assertIn("created_at", data)

        # 不应该包含的字段
        self.assertNotIn("email", data)
        self.assertNotIn("bio", data)

        print("✅ 测试通过: UserPublicSerializer 字段正确")

    def test_private_serializer_fields(self):
        """测试私有序列化器包含完整字段"""
        from apps.users.serializers import UserPrivateSerializer

        serializer = UserPrivateSerializer(self.user)
        data = serializer.data

        # 应该包含所有字段
        self.assertIn("id", data)
        self.assertIn("username", data)
        self.assertIn("email", data)
        self.assertIn("bio", data)
        self.assertIn("created_at", data)

        # 验证值
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["bio"], "Test bio")

        print("✅ 测试通过: UserPrivateSerializer 字段正确")
