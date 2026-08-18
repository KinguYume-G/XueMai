"""
N+1 查询优化性能测试

测试所有已优化的 ViewSet，确保查询次数符合预期目标。
"""

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.posts.models import Post, Bookmark, Tag
from apps.comments.models import Comment
from apps.social.models import Follow, ChatMessage
from apps.users.models import Profile

User = get_user_model()


class N1OptimizationTest(TestCase):
    """N+1 查询优化测试"""
    
    @classmethod
    def setUpTestData(cls):
        """
        创建测试数据（只执行一次）
        
        创建内容：
        - 1个主测试用户
        - 20个其他用户
        - 关注关系
        - 10个帖子
        - 30条评论（含回复）
        - 聊天消息
        """
        # 1. 创建主测试用户
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.get_or_create(user=cls.user)
        
        # 2. 创建其他测试用户（20个）
        cls.other_users = []
        for i in range(20):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            Profile.objects.get_or_create(user=user)
            cls.other_users.append(user)
        
        # 3. 创建关注关系（关注前10个用户）
        for i in range(10):
            Follow.objects.create(
                follower=cls.user,
                following=cls.other_users[i]
            )
        
        # 4. 创建粉丝关系（后5个用户关注我）
        for i in range(10, 15):
            Follow.objects.create(
                follower=cls.other_users[i],
                following=cls.user
            )
        
        # 5. 创建互相关注（好友，前3个用户）
        for i in range(3):
            Follow.objects.create(
                follower=cls.other_users[i],
                following=cls.user
            )
        
        # 6. 创建帖子（10个）
        cls.posts = []
        for i in range(10):
            post = Post.objects.create(
                author=cls.other_users[i % len(cls.other_users)],
                title=f'Test Post {i}',
                body=f'This is test post content {i}',
                visibility='public',
                is_published=True
            )
            cls.posts.append(post)
        
        # 7. 创建标签
        tag1 = Tag.objects.create(name='Python')
        tag2 = Tag.objects.create(name='Django')
        for post in cls.posts[:5]:
            post.tags.add(tag1, tag2)
        
        # 8. 创建评论（30条，包含回复）
        cls.comments = []
        for i in range(20):
            comment = Comment.objects.create(
                post=cls.posts[0],
                author=cls.other_users[i % len(cls.other_users)],
                content=f'Test comment {i}',
                parent=None
            )
            cls.comments.append(comment)
        
        # 9. 创建回复（每个顶级评论有1-2个回复）
        for i, parent_comment in enumerate(cls.comments[:10]):
            Comment.objects.create(
                post=cls.posts[0],
                author=cls.user,
                content=f'Reply to comment {i}',
                parent=parent_comment
            )
        
        # 10. 创建书签（前5个帖子）
        for post in cls.posts[:5]:
            Bookmark.objects.create(
                user=cls.user,
                post=post
            )
        
        # 11. 创建聊天消息（与前5个用户）
        for i in range(5):
            ChatMessage.objects.create(
                from_user=cls.user,
                to_user=cls.other_users[i],
                content=f'Hello user{i}',
                message_type='text'
            )
            ChatMessage.objects.create(
                from_user=cls.other_users[i],
                to_user=cls.user,
                content=f'Hi testuser',
                message_type='text'
            )
    
    def setUp(self):
        """每个测试前执行"""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def _print_queries(self, queries, test_name):
        """打印查询详情（调试用）"""
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"总查询次数: {len(queries)}")
        print(f"{'='*60}")
        for i, query in enumerate(queries, 1):
            print(f"\n查询 {i}:")
            print(query['sql'][:300])
            if len(query['sql']) > 300:
                print('...')
    
    def test_comment_list_queries(self):
        """
        测试评论列表的查询优化
        
        优化前：~150 次查询（100个评论）
        优化后：< 10 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f'/api/comments/?post={self.posts[0].id}')
        
        self.assertEqual(response.status_code, 200)
        
        # 断言查询次数
        query_count = len(queries)
        self.assertLess(
            query_count, 
            10,
            f"评论列表查询次数过多: {query_count} 次（目标 < 10）"
        )
        
        # 失败时打印详情
        if query_count >= 10:
            self._print_queries(queries, 'comment_list_queries')
    
    def test_comment_with_replies_queries(self):
        """
        测试带回复的评论查询优化
        
        优化前：~170 次查询（100个评论 + 50个回复）
        优化后：< 15 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                f'/api/comments/?post={self.posts[0].id}&with_replies=true'
            )
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            15,
            f"带回复评论查询次数过多: {query_count} 次（目标 < 15）"
        )
        
        if query_count >= 15:
            self._print_queries(queries, 'comment_with_replies_queries')
    
    def test_following_list_queries(self):
        """
        测试关注列表的查询优化
        
        优化前：~200 次查询（50个关注用户 * 4次查询/用户）
        优化后：< 10 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/chat/following/')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            10,
            f"关注列表查询次数过多: {query_count} 次（目标 < 10）"
        )
        
        if query_count >= 10:
            self._print_queries(queries, 'following_list_queries')
    
    def test_followers_list_queries(self):
        """
        测试粉丝列表的查询优化
        
        优化前：~200 次查询
        优化后：< 10 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/chat/followers/')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            10,
            f"粉丝列表查询次数过多: {query_count} 次（目标 < 10）"
        )
        
        if query_count >= 10:
            self._print_queries(queries, 'followers_list_queries')
    
    def test_friends_list_queries(self):
        """
        测试好友列表的查询优化
        
        优化前：~200 次查询
        优化后：< 10 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/chat/friends/')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            10,
            f"好友列表查询次数过多: {query_count} 次（目标 < 10）"
        )
        
        if query_count >= 10:
            self._print_queries(queries, 'friends_list_queries')
    
    def test_user_profile_queries(self):
        """
        测试用户资料页的查询优化
        
        优化前：~200 次查询（100个用户 * 2次查询/用户）
        优化后：< 5 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/users/')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            5,
            f"用户列表查询次数过多: {query_count} 次（目标 < 5）"
        )
        
        if query_count >= 5:
            self._print_queries(queries, 'user_profile_queries')
    
    def test_my_bookmarks_queries(self):
        """
        测试我的书签查询优化
        
        优化前：~N+5 次查询（N个书签）
        优化后：< 10 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/posts/my_bookmarks/')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            10,
            f"书签列表查询次数过多: {query_count} 次（目标 < 10）"
        )
        
        if query_count >= 10:
            self._print_queries(queries, 'my_bookmarks_queries')
    
    def test_post_feed_queries(self):
        """
        测试帖子 Feed 流的查询优化
        
        优化前：~500 次查询（100个帖子 * 5次查询/帖子）
        优化后：< 15 次查询
        """
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/posts/feed/?tab=hot')
        
        self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        self.assertLess(
            query_count, 
            15,
            f"帖子 Feed 查询次数过多: {query_count} 次（目标 < 15）"
        )
        
        if query_count >= 15:
            self._print_queries(queries, 'post_feed_queries')


class QueryCountSummaryTest(TestCase):
    """查询次数汇总测试（生成报告）"""
    
    def test_print_optimization_summary(self):
        """
        打印优化效果总结
        
        这不是一个真正的测试，而是用于生成优化报告
        """
        print("\n" + "="*60)
        print(" N+1 查询优化效果总结")
        print("="*60)
        print("\n预期查询次数目标：")
        print("  - 评论列表（无回复）: < 10 次")
        print("  - 评论列表（带回复）: < 15 次")
        print("  - 关注列表: < 10 次")
        print("  - 粉丝列表: < 10 次")
        print("  - 好友列表: < 10 次")
        print("  - 用户列表: < 5 次")
        print("  - 我的书签: < 10 次")
        print("  - 帖子 Feed: < 15 次")
        print("\n" + "="*60)
        print("运行 'python manage.py test tests.test_n1_optimization' 查看实际结果")
        print("="*60 + "\n")
        
        # 总是通过
        self.assertTrue(True)
