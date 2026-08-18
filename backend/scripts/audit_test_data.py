#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""审计数据库中的测试数据"""
import os
import sys
import django

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.models import User
from apps.posts.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from apps.bookmarks.models import Bookmark
from django.db.models import Q

print("\n" + "="*80)
print("学脉平台 - 数据库测试数据审计报告")
print("="*80)

# 测试数据关键词
TEST_KEYWORDS = ['test', 'Test', 'TEST', 'SEED', 'seed', '测试', 'Jeffrey', 'JEFFREY',
                 'Alice', 'alice', 'demo', 'Demo', 'DEMO', 'sample', 'Sample']

test_users = []
production_users = []
test_posts = []
production_posts = []
test_exchanges = []
production_exchanges = []
test_internships = []
production_internships = []
test_communities = []
production_communities = []

print("\n" + "="*80)
print("【1】用户数据审计")
print("="*80)

all_users = User.objects.all()
print(f"\n总用户数: {all_users.count()} 个\n")

for user in all_users:
    is_test = False
    reasons = []

    # 检查用户名
    for keyword in TEST_KEYWORDS:
        if keyword in user.username:
            is_test = True
            reasons.append(f"用户名包含'{keyword}'")
            break

    # 检查邮箱
    if not is_test:
        for keyword in TEST_KEYWORDS:
            if keyword in user.email:
                is_test = True
                reasons.append(f"邮箱包含'{keyword}'")
                break

    if is_test:
        test_users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'reason': ', '.join(reasons)
        })
    else:
        production_users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })

if test_users:
    print("【测试用户】（建议删除）:")
    for user in test_users:
        print(f"  [TEST] ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email']}")
        print(f"         原因: {user['reason']}")
else:
    print("未发现测试用户")

if production_users:
    print(f"\n【生产用户】（保留）: {len(production_users)} 个")
    for user in production_users[:5]:
        print(f"  [PROD] ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email']}")
    if len(production_users) > 5:
        print(f"  ... 还有 {len(production_users) - 5} 个生产用户")

# 审计帖子
print("\n" + "="*80)
print("【2】帖子数据审计")
print("="*80)

all_posts = Post.objects.all()
print(f"\n总帖子数: {all_posts.count()} 个\n")

for post in all_posts:
    is_test = False
    reasons = []

    # 检查标题
    title = post.title if hasattr(post, 'title') and post.title else ""
    content = post.content if hasattr(post, 'content') and post.content else ""

    for keyword in TEST_KEYWORDS:
        if keyword in title or keyword in content:
            is_test = True
            reasons.append(f"标题/内容包含'{keyword}'")
            break

    # 检查是否标题为空或内容过短
    if not is_test and (not title or len(content) < 50):
        is_test = True
        reasons.append("内容过短或标题为空")

    if is_test:
        test_posts.append({
            'id': post.id,
            'title': title[:50] + '...' if len(title) > 50 else title,
            'author': post.author.username if post.author else 'N/A',
            'reason': ', '.join(reasons)
        })
    else:
        production_posts.append({
            'id': post.id,
            'title': title[:50] + '...' if len(title) > 50 else title,
            'author': post.author.username if post.author else 'N/A'
        })

if test_posts:
    print("【测试帖子】（建议删除）:")
    for post in test_posts[:10]:
        print(f"  [TEST] ID: {post['id']}, 标题: {post['title']}, 作者: {post['author']}")
        print(f"         原因: {post['reason']}")
    if len(test_posts) > 10:
        print(f"  ... 还有 {len(test_posts) - 10} 个测试帖子")
else:
    print("未发现测试帖子")

if production_posts:
    print(f"\n【生产帖子】（保留）: {len(production_posts)} 个")
    for post in production_posts[:5]:
        print(f"  [PROD] ID: {post['id']}, 标题: {post['title']}, 作者: {post['author']}")
    if len(production_posts) > 5:
        print(f"  ... 还有 {len(production_posts) - 5} 个生产帖子")

# 审计交换项目
print("\n" + "="*80)
print("【3】交换项目数据审计")
print("="*80)

all_exchanges = ExchangeProgram.objects.all()
print(f"\n总交换项目数: {all_exchanges.count()} 个\n")

for exchange in all_exchanges:
    is_test = False
    reasons = []

    title = exchange.title if hasattr(exchange, 'title') and exchange.title else ""

    for keyword in TEST_KEYWORDS:
        if keyword in title:
            is_test = True
            reasons.append(f"标题包含'{keyword}'")
            break

    if is_test:
        test_exchanges.append({
            'id': exchange.id,
            'title': title,
            'university': exchange.university if hasattr(exchange, 'university') else 'N/A',
            'reason': ', '.join(reasons)
        })
    else:
        production_exchanges.append({
            'id': exchange.id,
            'title': title,
            'university': exchange.university if hasattr(exchange, 'university') else 'N/A'
        })

if test_exchanges:
    print("【测试交换项目】（建议删除）:")
    for ex in test_exchanges:
        print(f"  [TEST] ID: {ex['id']}, 标题: {ex['title']}, 大学: {ex['university']}")
        print(f"         原因: {ex['reason']}")
else:
    print("未发现测试交换项目")

if production_exchanges:
    print(f"\n【生产交换项目】（保留）: {len(production_exchanges)} 个")
    for ex in production_exchanges:
        print(f"  [PROD] ID: {ex['id']}, 标题: {ex['title']}, 大学: {ex['university']}")

# 审计实习
print("\n" + "="*80)
print("【4】实习数据审计")
print("="*80)

all_internships = Internship.objects.all()
print(f"\n总实习数: {all_internships.count()} 个\n")

for internship in all_internships:
    is_test = False
    reasons = []

    title = internship.title if hasattr(internship, 'title') and internship.title else ""

    for keyword in TEST_KEYWORDS:
        if keyword in title:
            is_test = True
            reasons.append(f"标题包含'{keyword}'")
            break

    if is_test:
        test_internships.append({
            'id': internship.id,
            'title': title,
            'company': internship.company if hasattr(internship, 'company') else 'N/A',
            'reason': ', '.join(reasons)
        })
    else:
        production_internships.append({
            'id': internship.id,
            'title': title,
            'company': internship.company if hasattr(internship, 'company') else 'N/A'
        })

if test_internships:
    print("【测试实习】（建议删除）:")
    for intern in test_internships[:10]:
        print(f"  [TEST] ID: {intern['id']}, 标题: {intern['title']}, 公司: {intern['company']}")
        print(f"         原因: {intern['reason']}")
    if len(test_internships) > 10:
        print(f"  ... 还有 {len(test_internships) - 10} 个测试实习")
else:
    print("未发现测试实习")

if production_internships:
    print(f"\n【生产实习】（保留）: {len(production_internships)} 个")
    for intern in production_internships[:5]:
        print(f"  [PROD] ID: {intern['id']}, 标题: {intern['title']}, 公司: {intern['company']}")
    if len(production_internships) > 5:
        print(f"  ... 还有 {len(production_internships) - 5} 个生产实习")

# 审计社区
print("\n" + "="*80)
print("【5】社区数据审计")
print("="*80)

all_communities = Community.objects.all()
print(f"\n总社区数: {all_communities.count()} 个\n")

for community in all_communities:
    is_test = False
    reasons = []

    name = community.name if hasattr(community, 'name') and community.name else ""

    for keyword in TEST_KEYWORDS:
        if keyword in name:
            is_test = True
            reasons.append(f"名称包含'{keyword}'")
            break

    if is_test:
        test_communities.append({
            'id': community.id,
            'name': name,
            'members': community.members if hasattr(community, 'members') else 0,
            'reason': ', '.join(reasons)
        })
    else:
        production_communities.append({
            'id': community.id,
            'name': name,
            'members': community.members if hasattr(community, 'members') else 0
        })

if test_communities:
    print("【测试社区】（建议删除）:")
    for comm in test_communities:
        print(f"  [TEST] ID: {comm['id']}, 名称: {comm['name']}, 成员数: {comm['members']}")
        print(f"         原因: {comm['reason']}")
else:
    print("未发现测试社区")

if production_communities:
    print(f"\n【生产社区】（保留）: {len(production_communities)} 个")
    for comm in production_communities:
        print(f"  [PROD] ID: {comm['id']}, 名称: {comm['name']}, 成员数: {comm['members']}")

# 审计收藏
print("\n" + "="*80)
print("【6】收藏数据审计")
print("="*80)

all_bookmarks = Bookmark.objects.all()
print(f"\n总收藏数: {all_bookmarks.count()} 个\n")

# 统计每个用户的收藏数
from collections import defaultdict
bookmarks_by_user = defaultdict(list)

for bookmark in all_bookmarks:
    bookmarks_by_user[bookmark.user.username].append({
        'type': bookmark.content_type,
        'object_id': bookmark.object_id
    })

print("收藏分布（按用户）:")
for username, bookmarks in bookmarks_by_user.items():
    print(f"  - {username}: {len(bookmarks)} 个收藏")
    type_count = defaultdict(int)
    for bm in bookmarks:
        type_count[bm['type']] += 1
    for content_type, count in type_count.items():
        print(f"      {content_type}: {count} 个")

# 汇总报告
print("\n" + "="*80)
print("【汇总统计】")
print("="*80)

print(f"\n测试数据统计（建议删除）:")
print(f"  - 测试用户: {len(test_users)} 个")
print(f"  - 测试帖子: {len(test_posts)} 个")
print(f"  - 测试交换项目: {len(test_exchanges)} 个")
print(f"  - 测试实习: {len(test_internships)} 个")
print(f"  - 测试社区: {len(test_communities)} 个")
print(f"  - 相关收藏: [需要用户确认]")

print(f"\n生产数据统计（保留）:")
print(f"  - 生产用户: {len(production_users)} 个")
print(f"  - 生产帖子: {len(production_posts)} 个")
print(f"  - 生产交换项目: {len(production_exchanges)} 个")
print(f"  - 生产实习: {len(production_internships)} 个")
print(f"  - 生产社区: {len(production_communities)} 个")

print("\n" + "="*80)
print("【重要提示】")
print("="*80)
print("\n在执行删除操作前，请仔细检查以上审计结果。")
print("确认哪些数据需要删除，哪些数据需要保留。")
print("\n建议:")
print("1. 如果所有测试数据都需要删除，请确认")
print("2. 如果某些数据需要保留（如某些用户或帖子实际上是真实数据），请明确指出")
print("3. 删除操作不可逆，请谨慎确认")
print("\n" + "="*80 + "\n")
