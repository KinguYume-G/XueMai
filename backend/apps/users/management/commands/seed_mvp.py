"""
生成MVP测试数据（幂等）
运行：python manage.py seed_mvp [--clear]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

from apps.campus.models import University, School
from apps.users.models import Profile
from apps.posts.models import Post, Tag, PostLike, Bookmark, Visibility
from apps.comments.models import Comment
from apps.social.models import Follow
from apps.notifications.models import Notification
from apps.opportunities.models import ExchangeProgram, Internship

User = get_user_model()
fake = Faker(["zh_CN", "en_US"])


class Command(BaseCommand):
    help = "生成MVP测试数据（幂等）"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="清空现有数据后再生成")

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("ℹ️  正在清理旧数据..."))
            self.clear_data()
            self.stdout.write(self.style.SUCCESS("✅ 数据清理完成"))

        self.stdout.write(self.style.SUCCESS("开始生成种子数据..."))

        # 1) 大学与学院
        universities = self.create_universities()
        schools = self.create_schools(universities)
        self.stdout.write(self.style.SUCCESS(f"✅ 大学 {len(universities)} 所，学院 {len(schools)} 个"))

        # 2) 标签
        tags = self.create_tags()
        self.stdout.write(self.style.SUCCESS(f"✅ 标签 {len(tags)} 个"))

        # 3) 用户与资料
        users = self.create_users(universities)
        self.stdout.write(self.style.SUCCESS(f"✅ 用户 {len(users)} 个（含资料）"))

        # 4) 关注
        follows_count = self.create_follows(users)
        self.stdout.write(self.style.SUCCESS(f"✅ 关注关系 {follows_count} 个"))

        # 5) 帖子
        posts = self.create_posts(users, tags)
        self.stdout.write(self.style.SUCCESS(f"✅ 帖子 {len(posts)} 条"))

        # 6) 点赞与收藏
        likes_count = self.create_likes(users, posts)
        bookmarks_count = self.create_bookmarks(users, posts)
        self.stdout.write(self.style.SUCCESS(f"✅ 点赞 {likes_count}，收藏 {bookmarks_count}"))

        # 7) 评论
        comments_count = self.create_comments(users, posts)
        self.stdout.write(self.style.SUCCESS(f"✅ 评论 {comments_count} 条"))

        # 8) 机会
        exchanges_count = self.create_exchange_programs(users, universities)
        internships_count = self.create_internships(users)
        self.stdout.write(self.style.SUCCESS(f"✅ 交换 {exchanges_count}，实习 {internships_count}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 种子数据生成完成！"))
        self.stdout.write(self.style.SUCCESS("\n可使用以下测试账号登录："))
        self.stdout.write("  用户名: alice, bob, charlie, david, emma ...")
        self.stdout.write("  密码: testpass123")

    # ---------------------- 清理数据 ----------------------
    def clear_data(self):
        # 按依赖顺序删除
        Bookmark.objects.all().delete()
        PostLike.objects.all().delete()
        Comment.objects.all().delete()
        Notification.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Follow.objects.all().delete()
        ExchangeProgram.objects.all().delete()
        Internship.objects.all().delete()
        Profile.objects.all().delete()
        School.objects.all().delete()
        University.objects.all().delete()
        
        # 清理可能残留的空 slug 记录
        Tag.objects.filter(slug='').delete()
        University.objects.filter(slug='').delete()
        School.objects.filter(slug='').delete()
        
        self.stdout.write('🧹 已清理空 slug 记录')

    # ---------------------- 数据创建 ----------------------
    def _universities_dataset(self):
        return [
            {
                "name": "北京大学",
                "country": "中国",
                "city": "北京",
                "schools": ["信息科学技术学院", "经济学院", "法学院"],
            },
            {
                "name": "清华大学",
                "country": "中国",
                "city": "北京",
                "schools": ["计算机科学与技术系", "经济管理学院", "美术学院"],
            },
            {
                "name": "National University of Singapore",
                "country": "Singapore",
                "city": "Singapore",
                "schools": ["School of Computing", "Business School", "Faculty of Law"],
            },
            {
                "name": "香港大学",
                "country": "中国香港",
                "city": "香港",
                "schools": ["工程学院", "商学院", "文学院"],
            },
            {
                "name": "东京大学",
                "country": "日本",
                "city": "东京",
                "schools": ["情報理工学系研究科", "経済学部", "法学部"],
            },
        ]

    def create_universities(self):
        universities = []
        for data in self._universities_dataset():
            uni, created = University.objects.get_or_create(
                name=data["name"],
                defaults={
                    "country": data["country"],
                    "city": data["city"],
                    "website": f"https://{data['name'].lower().replace(' ', '')}.edu",
                    "students_count": random.randint(10000, 50000),
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 大学创建: {uni.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️  大学已存在: {uni.name}"))
            universities.append(uni)
        return universities

    def create_schools(self, universities):
        name_to_uni = {u.name: u for u in universities}
        created_schools = []
        for data in self._universities_dataset():
            uni = name_to_uni.get(data["name"])  # 已存在
            for school_name in data["schools"]:
                school, created = School.objects.get_or_create(
                    university=uni,
                    name=school_name,
                    defaults={"students_count": random.randint(1000, 5000)},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ 学院创建: {uni.name} - {school.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"ℹ️  学院已存在: {uni.name} - {school.name}"))
                created_schools.append(school)
        return created_schools

    def create_tags(self):
        tag_names = [
            "学习",
            "生活",
            "交换",
            "实习",
            "求职",
            "考研",
            "出国",
            "编程",
            "设计",
            "摄影",
            "旅行",
            "美食",
            "运动",
            "音乐",
            "Python",
            "JavaScript",
            "AI",
            "机器学习",
            "数据分析",
        ]
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 标签创建: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️  标签已存在: {name}"))
            tags.append(tag)
        return tags

    def create_users(self, universities):
        usernames = [
            "alice",
            "bob",
            "charlie",
            "david",
            "emma",
            "frank",
            "grace",
            "henry",
            "iris",
            "jack",
        ]
        users = []
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "bio": fake.text(max_nb_chars=100),
                },
            )
            if created:
                user.set_password("testpass123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ 用户创建: {username}"))
            else:
                # 轻量更新非关键字段
                if not user.email:
                    user.email = f"{username}@example.com"
                    user.save()
                self.stdout.write(self.style.WARNING(f"ℹ️  用户已存在: {username}"))

            # 资料
            university = random.choice(universities)
            school = random.choice(list(university.schools.all())) if university.schools.exists() else None
            profile_defaults = {
                "university": university,
                "school": school,
                "major": random.choice(["计算机科学", "经济学", "法学", "工程", "商业管理"]),
                "grade": random.choice(["freshman", "sophomore", "junior", "senior", "master", "phd"]),
                "github_url": f"https://github.com/{username}",
            }
            Profile.objects.update_or_create(user=user, defaults=profile_defaults)
            users.append(user)

        # 回填社交与帖子计数
        for user in users:
            p = user.profile
            p.posts_count = Post.objects.filter(author=user).count()
            p.followers_count = Follow.objects.filter(following=user).count()
            p.following_count = Follow.objects.filter(follower=user).count()
            p.save()
        return users

    def create_follows(self, users):
        count = 0
        for user in users:
            num_following = 4  # 固定一些，提升幂等性
            potential = [u for u in users if u != user]
            following_users = potential[:num_following] if len(potential) >= num_following else potential
            for target in following_users:
                _, created = Follow.objects.get_or_create(follower=user, following=target)
                if created:
                    count += 1
        # 统一刷新计数
        for user in users:
            p = user.profile
            p.followers_count = Follow.objects.filter(following=user).count()
            p.following_count = Follow.objects.filter(follower=user).count()
            p.save()
        return count

    def create_posts(self, users, tags):
        posts = []
        # 为每个用户创建固定数量的帖子，标题使用确定性前缀，避免重复
        for user in users:
            for idx in range(1, 6):  # 每人 5 篇
                title = f"[SEED] {user.username} post {idx}"
                post, created = Post.objects.get_or_create(
                    author=user,
                    title=title,
                    defaults={
                        "body": fake.text(max_nb_chars=500),
                        "visibility": random.choice([v[0] for v in Visibility.choices]),
                        "is_published": True,
                        "target_university": user.profile.university if random.random() < 0.5 else None,
                        "views_count": random.randint(10, 1000),
                    },
                )
                # 绑定标签（确定性选择）
                if created or post.tags.count() == 0:
                    chosen = tags[: (idx % 4) + 1]
                    post.tags.set(chosen)
                # 计数刷新
                for tag in post.tags.all():
                    tag.posts_count = tag.posts.count()
                    tag.save()
                posts.append(post)

        # 刷新作者帖子数
        for user in users:
            p = user.profile
            p.posts_count = Post.objects.filter(author=user).count()
            p.save()
        return posts

    def create_likes(self, users, posts):
        count = 0
        for post in posts:
            # 每个帖子被前3个非作者用户点赞（确定性）
            likers = [u for u in users if u != post.author][:3]
            for u in likers:
                _, created = PostLike.objects.get_or_create(user=u, post=post)
                if created:
                    count += 1
            post.likes_count = PostLike.objects.filter(post=post).count()
            post.save()
        return count

    def create_bookmarks(self, users, posts):
        count = 0
        for user in users:
            # 每个用户收藏前2个非自己发布的帖子（确定性）
            to_bookmark = [p for p in posts if p.author != user][:2]
            for post in to_bookmark:
                _, created = Bookmark.objects.get_or_create(user=user, post=post)
                if created:
                    count += 1
                post.bookmarks_count = Bookmark.objects.filter(post=post).count()
                post.save()
        return count

    def create_comments(self, users, posts):
        count = 0
        for post in posts:
            # 前2位用户各发一条顶级评论（确定性）
            commenters = users[:2]
            for i, u in enumerate(commenters, start=1):
                content = f"[SEED] comment {i} on post {post.id} by {u.username}"
                comment, created = Comment.objects.get_or_create(
                    post=post,
                    author=u,
                    content=content,
                    defaults={},
                )
                if created:
                    count += 1
                # 一条回复
                reply_content = f"[SEED] reply to comment {comment.id}"
                _, created_reply = Comment.objects.get_or_create(
                    post=post,
                    author=post.author,
                    content=reply_content,
                    defaults={"parent": comment},
                )
                if created_reply:
                    count += 1
            post.comments_count = Comment.objects.filter(post=post, parent__isnull=True).count()
            post.save()
        return count

    def create_exchange_programs(self, users, universities):
        count = 0
        base_titles = [f"[SEED] {u.name} 交换项目" for u in universities[:10]]
        for idx, title in enumerate(base_titles, start=1):
            uni = universities[(idx - 1) % len(universities)]
            program, created = ExchangeProgram.objects.get_or_create(
                title=title,
                defaults={
                    "description": fake.text(max_nb_chars=300),
                    "host_university": uni,
                    "location": fake.city(),
                    "duration": random.choice(["一学期", "一学年", "暑期"]),
                    "deadline": timezone.now().date() + timedelta(days=90),
                    "requirements": fake.text(max_nb_chars=200),
                    "link": fake.url(),
                    "visibility": "public",
                    "is_published": True,
                    "posted_by": users[(idx - 1) % len(users)],
                    "views_count": random.randint(50, 500),
                },
            )
            if created:
                count += 1
        return count

    def create_internships(self, users):
        count = 0
        companies = ["腾讯", "阿里巴巴", "字节跳动", "Google", "Microsoft", "Amazon"]
        for idx in range(1, 16):
            title = f"[SEED] 实习岗位 {idx}"
            internship, created = Internship.objects.get_or_create(
                title=title,
                defaults={
                    "company": companies[(idx - 1) % len(companies)],
                    "description": fake.text(max_nb_chars=300),
                    "location": random.choice(["北京", "上海", "深圳", "杭州", "新加坡", "东京"]),
                    "type": random.choice(["full_time", "part_time", "internship", "remote"]),
                    "duration": random.choice(["3个月", "6个月", "1年"]),
                    "deadline": timezone.now().date() + timedelta(days=60),
                    "requirements": fake.text(max_nb_chars=200),
                    "salary_range": f"{random.randint(5, 15)}k-{random.randint(16, 30)}k",
                    "link": fake.url(),
                    "visibility": "public",
                    "is_published": True,
                    "posted_by": users[(idx - 1) % len(users)],
                    "views_count": random.randint(100, 800),
                },
            )
            if created:
                count += 1
        return count

