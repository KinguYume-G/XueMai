#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建真实的、有价值的数据 - 学脉平台"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.models import User, Profile
from apps.posts.models import Post, Tag
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from apps.bookmarks.models import Bookmark
from apps.campus.models import University, School

print("\n" + "="*80)
print("学脉平台 - 真实数据创建脚本")
print("="*80)

# ============================================================================
# 步骤 1: 创建/获取大学数据
# ============================================================================
print("\n[步骤 1] 创建大学数据...")

universities_data = [
    {
        'name': '新加坡国立大学',
        'country': 'Singapore',
        'city': 'Singapore',
        'website': 'https://www.nus.edu.sg',
        'description': '新加坡国立大学（National University of Singapore），简称NUS，是新加坡首屈一指的世界级顶尖大学。',
        'students_count': 40000
    },
    {
        'name': '南洋理工大学',
        'country': 'Singapore',
        'city': 'Singapore',
        'website': 'https://www.ntu.edu.sg',
        'description': '南洋理工大学（Nanyang Technological University），简称NTU，是新加坡的一所研究密集型大学。',
        'students_count': 33000
    },
    {
        'name': '香港大学',
        'country': 'Hong Kong',
        'city': 'Hong Kong',
        'website': 'https://www.hku.hk',
        'description': '香港大学（The University of Hong Kong），简称港大（HKU），是香港历史最悠久的高等教育机构。',
        'students_count': 30000
    },
    {
        'name': '香港科技大学',
        'country': 'Hong Kong',
        'city': 'Hong Kong',
        'website': 'https://www.ust.hk',
        'description': '香港科技大学（The Hong Kong University of Science and Technology），简称科大（HKUST），是一所亚洲顶尖、国际知名的研究型大学。',
        'students_count': 16000
    },
    {
        'name': '东京大学',
        'country': 'Japan',
        'city': 'Tokyo',
        'website': 'https://www.u-tokyo.ac.jp',
        'description': '东京大学（The University of Tokyo），简称东大，是日本排名最高的大学。',
        'students_count': 28000
    },
    {
        'name': '墨尔本大学',
        'country': 'Australia',
        'city': 'Melbourne',
        'website': 'https://www.unimelb.edu.au',
        'description': '墨尔本大学（The University of Melbourne）始建于1853年，是澳大利亚历史最悠久的大学之一。',
        'students_count': 51000
    },
    {
        'name': 'Asia Pacific University',
        'country': 'Malaysia',
        'city': 'Kuala Lumpur',
        'website': 'https://www.apu.edu.my',
        'description': 'Asia Pacific University (APU) is among Malaysia\'s Premier Private Universities.',
        'students_count': 13000
    },
]

universities = {}
for uni_data in universities_data:
    uni, created = University.objects.get_or_create(
        name=uni_data['name'],
        defaults={
            'country': uni_data['country'],
            'city': uni_data['city'],
            'website': uni_data['website'],
            'description': uni_data['description'],
            'students_count': uni_data['students_count']
        }
    )
    universities[uni_data['name']] = uni
    if created:
        print(f"[OK] 创建大学: {uni.name}")
    else:
        print(f"[INFO] 大学已存在: {uni.name}")

apu = universities['Asia Pacific University']

# ============================================================================
# 步骤 2: 为现有用户创建Profile
# ============================================================================
print("\n[步骤 2] 为现有用户创建Profile...")

users = list(User.objects.all())
print(f"当前有 {len(users)} 个用户")

majors = ['Computer Science', 'Software Engineering', 'Data Science', 'Business Analytics',
          'Information Technology', 'Business Administration', 'Marketing', 'Finance']
grades = ['sophomore', 'junior', 'senior', 'master']

for user in users:
    if not hasattr(user, 'profile') or user.profile is None:
        profile = Profile.objects.create(
            user=user,
            university=apu,
            major=random.choice(majors),
            grade=random.choice(grades),
            bio=f"{user.username} is a student at APU studying {random.choice(majors)}.",
            followers_count=random.randint(50, 500),
            following_count=random.randint(30, 300),
            posts_count=0
        )
        print(f"[OK] 创建Profile: {user.username}")
    else:
        print(f"[INFO] Profile已存在: {user.username}")

# ============================================================================
# 步骤 3: 创建真实的帖子
# ============================================================================
print("\n[步骤 3] 创建真实帖子...")

# 创建标签
tags_data = [
    '实习', '求职', '技术分享', '学习经验', '交换项目',
    'React', 'Python', 'JavaScript', 'Data Science', 'Machine Learning',
    'APU', '马来西亚', '新加坡', '香港', '留学'
]

tags = {}
for tag_name in tags_data:
    tag, created = Tag.objects.get_or_create(name=tag_name)
    tags[tag_name] = tag
    if created:
        print(f"[OK] 创建标签: {tag_name}")

# 真实帖子数据
posts_data = [
    {
        'title': '我在Google Malaysia实习的三个月总结',
        'body': '''大家好！我是APU Computer Science大三的学生，刚刚结束了在Google Malaysia为期三个月的软件工程实习。

**实习内容：**
我被分配到Google Cloud Platform团队，主要负责开发云服务的监控dashboard。使用的技术栈包括TypeScript、React、Go和Google Cloud的各种服务。

**技术收获：**
1. 学会了大规模分布式系统的设计模式
2. 深入理解了微服务架构
3. 掌握了Google内部的开发流程和工具
4. 代码审查经验大幅提升

**如何拿到offer：**
- 9月开始刷LeetCode，每天至少2题
- 10月投递简历
- 11月通过3轮技术面试 + 1轮HR面试
- 重点准备算法、系统设计和行为面试

**薪资待遇：**
实习生薪资RM 4500/月，提供免费午餐和班车服务。

如果大家有问题欢迎评论！''',
        'author_index': 0,
        'tags': ['实习', '求职', '技术分享', 'Google'],
        'likes_count': 342,
        'comments_count': 56,
        'views_count': 1850
    },
    {
        'title': '从零开始的React学习路线 | 前端开发入门指南',
        'body': '''作为一个从Python转React的开发者，我想分享一下我的学习经验。

**第一阶段：JavaScript基础（2周）**
- ES6语法：箭头函数、解构、模板字符串
- 异步编程：Promise、async/await
- 数组方法：map、filter、reduce

**第二阶段：React核心概念（3周）**
- 组件化思想
- JSX语法
- Props和State
- 生命周期 / Hooks
- 事件处理

**第三阶段：状态管理（2周）**
- Context API
- Redux / Zustand
- 数据流管理

**第四阶段：实战项目（4周）**
我做了一个Todo List、Weather App和个人博客。

**推荐资源：**
1. React官方文档（必读）
2. freeCodeCamp的React教程
3. Scrimba的交互式课程

现在我已经可以独立开发中等复杂度的前端项目了。学习编程最重要的是多写代码、多做项目！''',
        'author_index': 1,
        'tags': ['技术分享', 'React', 'JavaScript', '学习经验'],
        'likes_count': 268,
        'comments_count': 42,
        'views_count': 1420
    },
    {
        'title': '新加坡NUS交换一学期的真实体验',
        'body': '''刚刚结束在新加坡国立大学（NUS）为期一学期的交换，来分享一下真实体验。

**申请过程：**
- GPA要求：3.5以上
- 语言成绩：雅思6.5
- 申请材料：个人陈述、推荐信、成绩单
- 竞争很激烈，我们学校只有5个名额

**学习体验：**
NUS的课程强度确实比APU大，每周都有Quiz和Assignment。但教授都很nice，Office Hour都很耐心解答问题。我选了4门课：
1. Distributed Systems
2. Machine Learning
3. Cloud Computing
4. Database Systems

**生活成本：**
- 住宿：S$800/月（学校宿舍）
- 餐费：S$15-20/天
- 交通：S$100/月
总计大约S$1500/月

**收获：**
1. 认识了来自20多个国家的朋友
2. 参加了3个Hackathon
3. 拿到了NUS教授的推荐信
4. 开阔了视野，更了解新加坡的科技行业

强烈推荐大家抓住交换机会！''',
        'author_index': 2,
        'tags': ['交换项目', '新加坡', 'NUS', '留学'],
        'likes_count': 445,
        'comments_count': 78,
        'views_count': 2340
    },
    {
        'title': 'Final Year Project选题建议 | 计算机专业',
        'body': '''马上要开始FYP了，分享一些选题建议。

**热门方向：**

**1. AI/机器学习**
- 图像识别应用
- 自然语言处理
- 推荐系统
优点：就业前景好，学到的技能实用
缺点：需要GPU资源，数学要求高

**2. Web开发**
- 电商平台
- 社交网络
- 项目管理系统
优点：技术栈成熟，容易展示成果
缺点：创新性可能不足

**3. 移动应用**
- Flutter/React Native跨平台应用
- Android/iOS原生应用
优点：实用性强，可以发布到App Store
缺点：需要学习移动开发特有的概念

**4. 区块链**
- 智能合约
- DeFi应用
- NFT平台
优点：前沿技术，有创新性
缺点：复杂度高，就业机会相对少

**我的建议：**
1. 选择自己感兴趣的方向
2. 考虑就业市场需求
3. 评估技术难度
4. 确保能在规定时间内完成

大家的FYP打算做什么方向？''',
        'author_index': 3,
        'tags': ['学习经验', 'APU', 'Computer Science'],
        'likes_count': 189,
        'comments_count': 34,
        'views_count': 980
    },
    {
        'title': 'Python数据分析入门：从Pandas到可视化',
        'body': '''整理了一份Python数据分析的学习笔记，分享给大家。

**核心库：**

**1. Pandas**
```python
import pandas as pd

# 读取数据
df = pd.read_csv('data.csv')

# 数据清洗
df.dropna()  # 删除缺失值
df.fillna(0)  # 填充缺失值

# 数据分析
df.describe()  # 统计摘要
df.groupby('category').mean()  # 分组统计
```

**2. NumPy**
数值计算的基础库，提供高效的数组操作。

**3. Matplotlib / Seaborn**
数据可视化，制作各种图表。

**实战项目建议：**
1. 分析Kaggle数据集
2. 爬取网站数据并分析
3. 分析自己的社交媒体数据

**学习资源：**
- Python for Data Analysis (书籍)
- Kaggle Learn
- DataCamp

数据分析是现在最热门的技能之一，推荐大家学习！''',
        'author_index': 4,
        'tags': ['技术分享', 'Python', 'Data Science'],
        'likes_count': 312,
        'comments_count': 48,
        'views_count': 1650
    },
    {
        'title': 'APU周边美食推荐 | 学生党省钱攻略',
        'body': '''在APU读了2年，整理了周边的美食推荐！

**早餐：**
1. **校内Cafe**: Nasi Lemak (RM 4.5)，性价比最高
2. **TPM对面的Roti Canai档**: RM 3.5/份，很正宗

**午餐/晚餐：**
1. **Mixed Rice**: RM 6-8，可以自己选菜
2. **Subway**: RM 15左右，周三有优惠
3. **McDonald's**: RM 12-15，有学生优惠
4. **Sushi King**: RM 20-30，偶尔改善伙食

**奶茶/咖啡：**
1. **Tealive**: RM 6-8
2. **ZUS Coffee**: RM 8-12，咖啡很不错
3. **Family Mart**: RM 5，性价比高

**省钱小贴士：**
- 中午1-2点有些店有优惠
- 下载GrabFood/Foodpanda的优惠券
- 和朋友一起点可以share运费

欢迎补充！''',
        'author_index': 5,
        'tags': ['APU', 'Malaysia', '生活'],
        'likes_count': 523,
        'comments_count': 92,
        'views_count': 2890
    },
    {
        'title': '投了50份简历后，我总结的求职经验',
        'body': '''从9月开始找实习到现在，投了50+份简历，拿到了5个面试，最终收获2个offer。

**简历优化：**
1. **一页原则**: 简历不要超过1页
2. **量化成果**: 用数据说话
   - ❌ "提升了系统性能"
   - ✅ "将系统响应时间从2秒优化到0.5秒，提升75%"
3. **项目经验**: 3-4个代表性项目
4. **技能清单**: 分类列举（编程语言/框架/工具）

**面试准备：**
1. **技术面试**:
   - LeetCode刷题200+（Easy 100 + Medium 80 + Hard 20）
   - 系统设计：看Grokking the System Design Interview
2. **行为面试**:
   - 准备STAR法则的故事
   - 为什么选择这家公司（一定要认真调研）
3. **英语**: 练习技术问题的英文表达

**投递技巧：**
- 优先通过内推
- 仔细阅读JD，针对性修改简历
- 早投（很多公司招满就关闭申请）

**心态调整：**
- 投简历被拒是常态，不要气馁
- 每次面试后复盘总结
- 保持学习，提升硬实力

大家一起加油！''',
        'author_index': 6,
        'tags': ['求职', '实习', '经验分享'],
        'likes_count': 678,
        'comments_count': 115,
        'views_count': 3420
    },
    {
        'title': '如何平衡学习和社团活动？',
        'body': '''作为APU Computer Society的前任会长，来分享一下时间管理经验。

**我的经历：**
- 大一大二：参加3个社团
- 大二大三：担任Computer Society会长
- 同时保持GPA 3.7+

**时间管理技巧：**

**1. 优先级排序**
使用Eisenhower Matrix:
- 紧急且重要：考试、Deadline前的作业
- 重要不紧急：学习新技术、健身
- 紧急不重要：部分社团活动
- 不紧急不重要：刷短视频

**2. 时间块管理**
- 8AM-5PM: 上课和自习
- 6PM-8PM: 社团活动
- 9PM-11PM: 个人学习时间
- 周末：项目开发

**3. 学会说不**
不是所有活动都要参加，选择真正对自己有价值的。

**社团活动的价值：**
1. 培养领导力和组织能力
2. 扩大人脉
3. 简历上有东西可写
4. 锻炼沟通和演讲能力

**我的建议：**
- 大一可以多尝试不同社团
- 大二选择1-2个深度参与
- 大三大四专注学习和求职

大学不只是学习，软技能也很重要！''',
        'author_index': 7,
        'tags': ['APU', '学习经验', '大学生活'],
        'likes_count': 234,
        'comments_count': 45,
        'views_count': 1280
    }
]

created_posts = []
for i, post_data in enumerate(posts_data):
    author = users[post_data['author_index'] % len(users)]

    # 随机生成创建时间（最近1-3个月）
    days_ago = random.randint(1, 90)
    created_at = datetime.now() - timedelta(days=days_ago)

    post = Post.objects.create(
        author=author,
        title=post_data['title'],
        body=post_data['body'],
        visibility='public',
        is_published=True,
        likes_count=post_data['likes_count'],
        comments_count=post_data['comments_count'],
        views_count=post_data['views_count']
    )

    # 添加标签
    for tag_name in post_data['tags']:
        if tag_name in tags:
            post.tags.add(tags[tag_name])

    created_posts.append(post)
    print(f"[OK] 创建帖子: {post.title[:50]}... (作者: {author.username})")

print(f"总共创建了 {len(created_posts)} 个帖子")

# ============================================================================
# 步骤 4: 创建真实的交换项目
# ============================================================================
print("\n[步骤 4] 创建交换项目...")

exchange_programs_data = [
    {
        'title': '2025春季新加坡国立大学交换项目',
        'host_university': '新加坡国立大学',
        'description': '''新加坡国立大学（NUS）2025年春季学期交换项目现正开放申请。

**项目时间：** 2025年1月 - 2025年5月（一学期）

**申请要求：**
- GPA 3.5及以上
- 雅思6.5或托福90以上
- 在读本科生或研究生
- 无不良学术记录

**学习内容：**
可选修计算机、工程、商科、人文等各学院课程。所修学分可转回本校。

**项目费用：**
- 学费：S$8,000/学期
- 住宿：S$800-1200/月
- 生活费：S$800-1000/月

**奖学金机会：**
表现优异的学生可申请NUS Global Relations奖学金（最高覆盖50%学费）。

**如何申请：**
1. 在线提交申请表
2. 上传成绩单和语言成绩
3. 提交个人陈述和推荐信
4. 等待面试通知

往期学生评价：课程质量高，国际化氛围浓厚，值得体验！''',
        'location': 'Singapore',
        'duration': '1学期（4-5个月）',
        'deadline_days': 45,  # 45天后截止
        'requirements': 'GPA 3.5+, 雅思6.5/托福90+',
        'country': 'Singapore',
        'tuition': 'S$8,000/学期',
        'gpa_min': '3.5',
        'lang_req': '雅思≥6.5 或 托福≥90',
        'rating_avg': 4.8,
        'rating_count': 234,
        'applied_count': 567,
        'cover_url': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800',
        'is_urgent': False
    },
    {
        'title': '香港大学2025秋季交换计划',
        'host_university': '香港大学',
        'description': '''香港大学（HKU）2025年秋季学期交换计划欢迎亚太地区优秀学生申请。

**项目亮点：**
- 世界排名Top 30大学
- 粤港澳大湾区核心城市
- 英语教学环境
- 丰富的实习机会

**可选专业：**
商学院、工程学院、社会科学学院、理学院等

**申请条件：**
- 本科大二及以上年级
- GPA 3.3及以上
- 英语水平：雅思6.5或托福85
- 个人陈述突出学术兴趣

**费用预算：**
- 学费：HK$42,000/学期
- 宿舍：HK$7,000-9,000/月
- 生活费：HK$5,000-8,000/月

**申请流程：**
在线申请 → 材料审核 → 视频面试 → 录取通知

HKU是拓展国际视野、体验香港文化的绝佳机会！''',
        'location': 'Hong Kong',
        'duration': '1学期（4个月）',
        'deadline_days': 60,
        'requirements': 'GPA 3.3+, 雅思6.5/托福85+',
        'country': 'Hong Kong',
        'tuition': 'HK$42,000/学期',
        'gpa_min': '3.3',
        'lang_req': '雅思≥6.5 或 托福≥85',
        'rating_avg': 4.7,
        'rating_count': 189,
        'applied_count': 423,
        'cover_url': 'https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=800',
        'is_urgent': False
    },
    {
        'title': '东京大学2025暑期研究项目',
        'host_university': '东京大学',
        'description': '''东京大学（UTokyo）暑期研究项目为期8周，专为对日本科技和文化感兴趣的学生设计。

**项目特色：**
- 由东京大学教授指导的研究项目
- 深入日本科技企业参访
- 日语语言课程
- 文化体验活动

**研究方向：**
- 人工智能与机器学习
- 机器人技术
- 可持续能源
- 生物医学工程

**申请要求：**
- 理工科背景
- GPA 3.4及以上
- 英语流利（部分项目需要基础日语）
- 研究兴趣陈述

**项目费用：**
- 项目费：¥350,000（约US$2,500）
- 住宿：¥80,000/月
- 生活费：¥60,000/月

**注意：** 提供部分奖学金名额，优秀申请者可获全额资助。

这是了解日本科技前沿、体验东京生活的宝贵机会！''',
        'location': 'Tokyo, Japan',
        'duration': '8周（暑期）',
        'deadline_days': 75,
        'requirements': 'GPA 3.4+, 理工科背景, 英语流利',
        'country': 'Japan',
        'tuition': '¥350,000（含住宿补贴）',
        'gpa_min': '3.4',
        'lang_req': '托福≥85 或 雅思≥6.0',
        'rating_avg': 4.9,
        'rating_count': 156,
        'applied_count': 312,
        'cover_url': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
        'is_urgent': False
    },
    {
        'title': '墨尔本大学2025-2026年度交换项目',
        'host_university': '墨尔本大学',
        'description': '''墨尔本大学（UniMelb）年度交换项目，体验澳大利亚顶尖大学的学术氛围。

**项目时长：**
可选择一学期或一学年（2025年7月 - 2026年6月）

**学术优势：**
- 澳洲排名第一大学
- 世界级研究设施
- 小班教学，师生比例高
- 学分全球认可

**热门专业：**
商科、计算机、工程、生物医学、设计

**申请条件：**
- GPA 3.2及以上
- 雅思7.0或托福94
- 完成至少一年本科学习
- 学术推荐信2封

**费用说明：**
- 学费：AU$15,000-18,000/学期
- 住宿：AU$1,200-1,800/月
- 生活费：AU$1,500/月
- 医疗保险：AU$600/年

**额外福利：**
- 免费使用大学健身房和图书馆
- 参加墨尔本各类文化活动
- 可兼职工作（每周最多20小时）

体验南半球的精彩学术生活！''',
        'location': 'Melbourne, Australia',
        'duration': '1-2学期',
        'deadline_days': 90,
        'requirements': 'GPA 3.2+, 雅思7.0/托福94+',
        'country': 'Australia',
        'tuition': 'AU$15,000-18,000/学期',
        'gpa_min': '3.2',
        'lang_req': '雅思≥7.0 或 托福≥94',
        'rating_avg': 4.6,
        'rating_count': 203,
        'applied_count': 489,
        'cover_url': 'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=800',
        'is_urgent': False
    },
    {
        'title': '南洋理工大学AI研究实习项目',
        'host_university': '南洋理工大学',
        'description': '''NTU人工智能研究院推出为期6个月的研究实习项目，专注于前沿AI技术。

**研究领域：**
- 计算机视觉
- 自然语言处理
- 强化学习
- AI伦理与安全

**项目内容：**
- 参与真实研究项目
- 发表学术论文机会
- 接触最新AI技术和工具
- 与世界级研究者合作

**申请要求：**
- 计算机/数学/工程相关专业
- GPA 3.6及以上
- 熟悉Python和深度学习框架（TensorFlow/PyTorch）
- 有研究经历或项目经验优先

**项目福利：**
- 月津贴：S$2,500
- 免费住宿
- 研究设备和GPU资源
- 研究成果可用于FYP或研究生申请

**申请材料：**
- 个人简历
- 研究兴趣陈述
- 2封学术推荐信
- 以往项目或论文（如有）

这是进入AI研究领域的黄金机会！''',
        'location': 'Singapore',
        'duration': '6个月',
        'deadline_days': 30,  # 即将截止
        'requirements': 'GPA 3.6+, CS/Math/Engineering, Python+深度学习',
        'country': 'Singapore',
        'tuition': '免学费（提供S$2,500/月津贴）',
        'gpa_min': '3.6',
        'lang_req': '雅思≥6.5 或 托福≥90',
        'rating_avg': 4.9,
        'rating_count': 127,
        'applied_count': 856,
        'cover_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800',
        'is_urgent': True  # 即将截止
    }
]

created_exchanges = []
for exchange_data in exchange_programs_data:
    host_uni = universities[exchange_data['host_university']]
    poster = random.choice(users)

    deadline = datetime.now().date() + timedelta(days=exchange_data['deadline_days'])

    exchange = ExchangeProgram.objects.create(
        title=exchange_data['title'],
        description=exchange_data['description'],
        host_university=host_uni,
        location=exchange_data['location'],
        duration=exchange_data['duration'],
        deadline=deadline,
        requirements=exchange_data['requirements'],
        country=exchange_data['country'],
        tuition=exchange_data['tuition'],
        gpa_min=exchange_data['gpa_min'],
        lang_req=exchange_data['lang_req'],
        rating_avg=exchange_data['rating_avg'],
        rating_count=exchange_data['rating_count'],
        applied_count=exchange_data['applied_count'],
        cover_url=exchange_data['cover_url'],
        is_urgent=exchange_data['is_urgent'],
        website=host_uni.website,
        visibility='public',
        is_published=True,
        posted_by=poster
    )
    created_exchanges.append(exchange)
    print(f"[OK] 创建交换项目: {exchange.title}")

print(f"总共创建了 {len(created_exchanges)} 个交换项目")

# ============================================================================
# 步骤 5: 创建真实的实习机会
# ============================================================================
print("\n[步骤 5] 创建实习机会...")

internships_data = [
    {
        'title': 'Software Engineer Intern',
        'company': 'Google Malaysia',
        'description': '''Google Malaysia is seeking talented Software Engineering interns to join our team for Summer 2025.

**Responsibilities:**
- Design and implement scalable backend services
- Collaborate with engineers across different teams
- Write clean, maintainable code
- Participate in code reviews
- Contribute to Google's products used by millions

**Technical Stack:**
- Languages: Go, Java, Python, C++
- Cloud: Google Cloud Platform
- Tools: Git, Bazel, internal Google tools

**What You'll Gain:**
- Hands-on experience with large-scale distributed systems
- Mentorship from world-class engineers
- Exposure to Google's engineering culture
- Potential for full-time conversion
- Networking opportunities

**Duration:** 12 weeks (June - August 2025)

**Location:** Google Malaysia Office, Kuala Lumpur''',
        'location': 'Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '12 weeks',
        'deadline_days': 35,
        'requirements': '''- Currently pursuing Bachelor's or Master's in Computer Science or related field
- Strong foundation in data structures and algorithms
- Proficiency in at least one programming language (Java/Python/C++/Go)
- GPA 3.5 or above
- Excellent problem-solving skills
- Good communication and teamwork abilities''',
        'salary_min': 4500,
        'salary_max': 5500,
        'remote': False,
        'skills': ['Python', 'Java', 'Go', 'Data Structures', 'Algorithms', 'System Design']
    },
    {
        'title': 'Data Analyst Intern',
        'company': 'Grab',
        'description': '''Grab is looking for a Data Analyst Intern to join our GrabFood team in Kuala Lumpur.

**What You'll Do:**
- Analyze user behavior and transaction data
- Create dashboards and reports using SQL and Tableau
- Provide data-driven insights to product teams
- Conduct A/B testing analysis
- Work on merchant and consumer analytics

**Tools & Technologies:**
- SQL (BigQuery, Presto)
- Python (Pandas, NumPy)
- Tableau / Looker
- Excel
- Git

**Projects You Might Work On:**
- Optimizing delivery routes
- Improving merchant onboarding conversion
- Analyzing pricing strategies
- Customer segmentation

**Why Grab:**
- Work on SEA's leading super app
- Real impact on millions of users
- Fast-paced startup environment
- Great team culture
- Free GrabFood credits!

**Duration:** 6 months

**Location:** Grab Tower, Kuala Lumpur (Hybrid - 3 days WFH)''',
        'location': 'Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '6 months',
        'deadline_days': 42,
        'requirements': '''- Pursuing degree in Statistics, Mathematics, Economics, Computer Science or related field
- Strong SQL skills
- Experience with Python for data analysis
- Familiar with statistical concepts
- Excellent analytical and problem-solving skills
- Good presentation skills''',
        'salary_min': 3000,
        'salary_max': 4000,
        'remote': True,
        'skills': ['SQL', 'Python', 'Tableau', 'Excel', 'Data Analysis', 'Statistics']
    },
    {
        'title': 'Frontend Developer Intern',
        'company': 'Shopee Malaysia',
        'description': '''Join Shopee's Frontend team and help build features used by millions of shoppers daily!

**Responsibilities:**
- Develop new features for Shopee web platform
- Optimize web performance and user experience
- Work with designers to implement pixel-perfect UIs
- Write clean, reusable React components
- Participate in sprint planning and daily standups

**Tech Stack:**
- React.js / Next.js
- TypeScript
- Redux / React Query
- Tailwind CSS / Styled Components
- Webpack / Vite

**Learning Opportunities:**
- Modern frontend architecture
- Performance optimization techniques
- Micro-frontend patterns
- A/B testing implementation
- Agile development workflow

**Perks:**
- Competitive stipend
- Free lunch and snacks
- Access to Shopee office facilities
- Intern activities and events
- Shopee vouchers

**Duration:** 3-6 months (flexible)

**Location:** Selangor (Near LRT)''',
        'location': 'Petaling Jaya, Selangor',
        'city': 'Petaling Jaya',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '3-6 months',
        'deadline_days': 50,
        'requirements': '''- Studying Computer Science, Software Engineering or related field
- Strong knowledge of JavaScript/TypeScript
- Experience with React.js
- Understanding of HTML5, CSS3, and responsive design
- Familiarity with Git
- Portfolio or GitHub projects (bonus)''',
        'salary_min': 2800,
        'salary_max': 3500,
        'remote': False,
        'skills': ['React', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Git', 'Frontend Development']
    },
    {
        'title': 'Backend Engineer Intern',
        'company': 'ByteDance Malaysia',
        'description': '''ByteDance (parent company of TikTok) is hiring Backend Engineering interns in Malaysia.

**What You'll Build:**
- RESTful APIs for TikTok features
- Microservices architecture
- Real-time data processing systems
- Database optimization
- Cloud infrastructure

**Technologies:**
- Go / Java / Python
- MySQL / Redis / MongoDB
- Kafka / RabbitMQ
- Docker / Kubernetes
- AWS / GCP

**Mentorship:**
- 1-on-1 mentor from senior engineers
- Technical training sessions
- Code review culture
- Career development guidance

**Impact:**
- Work on features used by 1 billion+ users
- Contribute to real production code
- Solve challenging scalability problems

**Office Culture:**
- Young, energetic team
- Flat organizational structure
- Free meals and beverages
- Game room and relaxation area

**Duration:** 6 months

**Location:** Kuala Lumpur''',
        'location': 'Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '6 months',
        'deadline_days': 38,
        'requirements': '''- Bachelor's/Master's student in Computer Science or related major
- Solid programming skills in Go, Java, or Python
- Understanding of OOP and design patterns
- Knowledge of databases and SQL
- Familiar with Linux/Unix systems
- GPA 3.3 or above''',
        'salary_min': 4000,
        'salary_max': 5000,
        'remote': False,
        'skills': ['Go', 'Java', 'Python', 'Microservices', 'Database', 'Docker', 'Kubernetes']
    },
    {
        'title': 'Cloud Solutions Intern',
        'company': 'Microsoft Malaysia',
        'description': '''Microsoft Malaysia is seeking Cloud Solutions interns to support our Azure customers.

**Role Overview:**
Help enterprise customers migrate to and optimize their Azure infrastructure.

**Responsibilities:**
- Assist in Azure deployment projects
- Create technical documentation
- Develop automation scripts
- Support customer workshops
- Learn cloud architecture patterns

**Technologies You'll Use:**
- Microsoft Azure (VMs, App Services, Functions)
- Azure DevOps
- PowerShell / Azure CLI
- Python / C#
- Terraform / ARM Templates

**Career Development:**
- Microsoft certifications (sponsored)
- Training on Azure, AI, and emerging tech
- Access to Microsoft Learn
- Global networking opportunities
- Potential for full-time offer

**Work Environment:**
- Flexible working hours
- Remote work options
- Modern office with collaboration spaces
- Diversity and inclusion culture

**Duration:** 6-12 months

**Location:** Kuala Lumpur (Hybrid)''',
        'location': 'Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '6-12 months',
        'deadline_days': 55,
        'requirements': '''- Pursuing degree in Computer Science, IT or related field
- Interest in cloud computing and DevOps
- Basic programming knowledge (Python/PowerShell/C#)
- Good communication skills (English)
- Eagerness to learn new technologies
- Customer-focused mindset''',
        'salary_min': 3500,
        'salary_max': 4200,
        'remote': True,
        'skills': ['Azure', 'Cloud Computing', 'DevOps', 'PowerShell', 'Python', 'Infrastructure']
    },
    {
        'title': 'Mobile App Developer Intern',
        'company': 'Touch n Go',
        'description': '''Touch 'n Go eWallet is Malaysia's leading mobile payment platform. Join our mobile team!

**What You'll Do:**
- Develop features for iOS/Android app
- Fix bugs and improve app performance
- Implement UI/UX designs
- Integrate with backend APIs
- Write unit and integration tests

**Tech Stack:**
- Flutter / React Native
- Native iOS (Swift) / Android (Kotlin)
- RESTful APIs
- Firebase
- Git / CI/CD

**Projects:**
- Payment features
- Rewards and loyalty programs
- QR code scanning
- Wallet management
- Push notifications

**What Makes Us Special:**
- Work on Malaysia's #1 e-wallet
- Fintech experience
- Agile team environment
- Learning budget for courses
- Latest Mac/PC provided

**Duration:** 3-6 months

**Location:** Bangsar South, Kuala Lumpur''',
        'location': 'Bangsar South, Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '3-6 months',
        'deadline_days': 45,
        'requirements': '''- Currently pursuing degree in Computer Science or Software Engineering
- Experience with Flutter, React Native, or native mobile development
- Understanding of mobile app architecture
- Familiar with REST APIs
- Git version control
- Portfolio of mobile apps (bonus)''',
        'salary_min': 2500,
        'salary_max': 3200,
        'remote': False,
        'skills': ['Flutter', 'React Native', 'iOS', 'Android', 'Mobile Development', 'Firebase']
    },
    {
        'title': 'Machine Learning Intern',
        'company': 'Petronas Digital',
        'description': '''PETRONAS Digital is seeking ML interns to work on AI projects in the energy sector.

**Exciting Projects:**
- Predictive maintenance using sensor data
- Computer vision for equipment inspection
- NLP for document processing
- Time series forecasting
- Anomaly detection systems

**Technical Stack:**
- Python (TensorFlow, PyTorch, Scikit-learn)
- Jupyter Notebooks
- MLOps tools (MLflow, Kubeflow)
- Cloud platforms (Azure ML, AWS SageMaker)
- Big Data tools (Spark)

**What You'll Learn:**
- End-to-end ML pipeline development
- Model deployment and monitoring
- Working with real industrial data
- Collaboration with domain experts
- Best practices in ML engineering

**Unique Opportunity:**
- Apply AI to solve real-world industry problems
- Work with cutting-edge technology
- Exposure to oil & gas domain
- Competitive compensation
- Potential for return offer

**Duration:** 6 months

**Location:** KLCC, Kuala Lumpur''',
        'location': 'KLCC, Kuala Lumpur',
        'city': 'Kuala Lumpur',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '6 months',
        'deadline_days': 60,
        'requirements': '''- Pursuing degree in Computer Science, Data Science, Mathematics or related field
- Strong Python programming skills
- Experience with machine learning frameworks
- Understanding of ML algorithms and statistics
- Familiarity with data preprocessing and feature engineering
- GPA 3.4 or above''',
        'salary_min': 3800,
        'salary_max': 4500,
        'remote': False,
        'skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Science', 'MLOps']
    },
    {
        'title': 'UI/UX Design Intern',
        'company': 'Airasia',
        'description': '''AirAsia is looking for a creative UI/UX Design Intern to join our Product Design team.

**Your Role:**
- Design mobile and web interfaces
- Create wireframes and prototypes
- Conduct user research and testing
- Collaborate with product managers and developers
- Maintain design system
- Create visual assets and illustrations

**Tools You'll Use:**
- Figma (primary)
- Adobe Creative Suite
- Principle / Framer for animations
- Miro for workshops
- Maze / UserTesting for research

**Design Projects:**
- Booking flow optimization
- Loyalty program redesign
- In-flight entertainment app
- AirAsia Super App features

**Why AirAsia:**
- Work on products used by millions of travelers
- Collaborative design culture
- Mentorship from senior designers
- Travel discounts
- Vibrant office environment

**Duration:** 3-6 months

**Location:** RedQ, Sepang (shuttle bus provided)''',
        'location': 'Sepang, Selangor',
        'city': 'Sepang',
        'country': 'Malaysia',
        'type': 'internship',
        'duration': '3-6 months',
        'deadline_days': 40,
        'requirements': '''- Studying Design, HCI, or related field
- Strong portfolio showcasing UI/UX projects
- Proficiency in Figma
- Understanding of design principles
- User-centered design mindset
- Good communication skills
- Passion for travel (bonus!)''',
        'salary_min': 2200,
        'salary_max': 2800,
        'remote': False,
        'skills': ['UI/UX Design', 'Figma', 'Adobe XD', 'Prototyping', 'User Research', 'Visual Design']
    }
]

created_internships = []
for internship_data in internships_data:
    poster = random.choice(users)
    deadline = datetime.now().date() + timedelta(days=internship_data['deadline_days'])

    internship = Internship.objects.create(
        title=internship_data['title'],
        company=internship_data['company'],
        description=internship_data['description'],
        location=internship_data['location'],
        city=internship_data['city'],
        country=internship_data['country'],
        type=internship_data['type'],
        duration=internship_data['duration'],
        deadline=deadline,
        requirements=internship_data['requirements'],
        salary_min=internship_data['salary_min'],
        salary_max=internship_data['salary_max'],
        salary_range=f"RM {internship_data['salary_min']} - {internship_data['salary_max']}/month",
        remote=internship_data['remote'],
        skills=internship_data['skills'],
        visibility='public',
        is_published=True,
        posted_by=poster
    )
    created_internships.append(internship)
    print(f"[OK] 创建实习: {internship.title} at {internship.company}")

print(f"总共创建了 {len(created_internships)} 个实习机会")

# ============================================================================
# 步骤 6: 创建更多真实社区
# ============================================================================
print("\n[步骤 6] 创建社区...")

# 检查现有社区
existing_communities = Community.objects.count()
print(f"当前有 {existing_communities} 个社区")

new_communities_data = [
    {
        'name': 'APU Computer Science 学习小组',
        'description': '''专注于计算机科学学习交流的社区。

我们的活动：
- 每周编程题目讨论
- 技术分享会
- Hackathon组队
- FYP互助
- 面试准备小组

加入我们，一起提升编程技能！''',
        'category': 'study_group',
        'members': 486,
        'activity_rate': 0.89
    },
    {
        'name': 'Data Science & AI 研究社',
        'description': '''专注于数据科学和人工智能学习的社区。

社区内容：
- Kaggle竞赛组队
- 机器学习项目分享
- 论文研讨会
- 数据分析工作坊
- 行业专家讲座

欢迎对AI感兴趣的同学加入！''',
        'category': 'study_group',
        'members': 352,
        'activity_rate': 0.82
    },
    {
        'name': 'APU 职业规划与求职交流群',
        'description': '''帮助学生规划职业发展、分享求职经验。

我们提供：
- 简历修改建议
- 模拟面试
- 内推信息分享
- 求职经验交流
- 职业导师对接

找工作不迷茫，加入我们！''',
        'category': 'interest',
        'members': 623,
        'activity_rate': 0.91
    },
    {
        'name': '留学交换经验分享社',
        'description': '''为计划出国交换或留学的同学提供信息和经验分享。

社区特色：
- 交换项目申请经验
- 各国大学介绍
- 签证办理指南
- 生活成本分享
- 学长学姐答疑

让你的留学申请不再困难！''',
        'category': 'interest',
        'members': 445,
        'activity_rate': 0.76
    },
    {
        'name': 'APU 创业者俱乐部',
        'description': '''连接有创业想法的学生，分享创业资源。

俱乐部活动：
- 创业想法pitch练习
- 商业计划书辅导
- 投资人对接
- 创业团队组建
- Startup Weekend

有想法就来实现它！''',
        'category': 'interest',
        'members': 234,
        'activity_rate': 0.68
    },
    {
        'name': 'APU 美食探索团',
        'description': '''探索马来西亚美食，分享餐厅推荐。

我们的活动：
- 每周美食打卡
- 餐厅团购优惠
- 烹饪技能交流
- 外卖优惠信息
- 聚餐活动组织

吃货们的天堂！''',
        'category': 'interest',
        'members': 789,
        'activity_rate': 0.85
    },
    {
        'name': 'APU 运动健身社',
        'description': '''推广健康生活方式，组织运动活动。

社团活动：
- 羽毛球/篮球/足球约球
- 健身房团练
- 跑步小组
- 运动挑战赛
- 运动装备团购

一起变得更健康！''',
        'category': 'interest',
        'members': 567,
        'activity_rate': 0.79
    },
    {
        'name': '马来西亚旅游爱好者',
        'description': '''探索马来西亚的美景，组织周末旅行。

社区特色：
- 周末短途旅行
- 景点攻略分享
- 拼车拼团
- 摄影技巧交流
- 旅行装备推荐

一起探索大马之美！''',
        'category': 'city',
        'city': 'Kuala Lumpur',
        'members': 412,
        'activity_rate': 0.73
    }
]

for comm_data in new_communities_data:
    creator = random.choice(users)

    try:
        comm, created = Community.objects.get_or_create(
            name=comm_data['name'],
            defaults={
                'description': comm_data['description'],
                'category': comm_data['category'],
                'city': comm_data.get('city', ''),
                'is_oncampus': comm_data['category'] == 'oncampus',
                'is_study_group': comm_data['category'] == 'study_group',
                'members': comm_data['members'],
                'activity_rate': comm_data['activity_rate'],
                'created_by': creator
            }
        )
        if created:
            print(f"[OK] 创建社区: {comm.name}")
        else:
            print(f"[INFO] 社区已存在: {comm.name}")
    except Exception as e:
        print(f"[SKIP] 跳过社区: {comm_data['name']} (原因: slug冲突)")

total_communities = Community.objects.count()
print(f"现在总共有 {total_communities} 个社区")

# ============================================================================
# 步骤 7: 为用户创建收藏关系
# ============================================================================
print("\n[步骤 7] 创建收藏关系...")

# 为每个用户随机创建3-8个收藏
all_posts = list(Post.objects.all())
all_exchanges = list(ExchangeProgram.objects.all())
all_internships = list(Internship.objects.all())
all_communities = list(Community.objects.all())

total_bookmarks = 0

for user in users:
    num_bookmarks = random.randint(3, 8)
    bookmarked = set()  # 避免重复收藏

    for _ in range(num_bookmarks):
        # 随机选择收藏类型
        content_types = []
        if all_posts:
            content_types.append('post')
        if all_exchanges:
            content_types.append('exchange')
        if all_internships:
            content_types.append('internship')
        if all_communities:
            content_types.append('community')

        if not content_types:
            break

        content_type = random.choice(content_types)

        # 根据类型选择对象
        if content_type == 'post':
            obj = random.choice(all_posts)
        elif content_type == 'exchange':
            obj = random.choice(all_exchanges)
        elif content_type == 'internship':
            obj = random.choice(all_internships)
        else:  # community
            obj = random.choice(all_communities)

        # 检查是否已经收藏过
        bookmark_key = (content_type, obj.id)
        if bookmark_key in bookmarked:
            continue

        # 创建收藏
        try:
            Bookmark.objects.create(
                user=user,
                content_type=content_type,
                object_id=obj.id
            )
            bookmarked.add(bookmark_key)
            total_bookmarks += 1
        except:
            # 如果重复就跳过
            pass

    print(f"[OK] 为用户 {user.username} 创建了 {len(bookmarked)} 个收藏")

print(f"总共创建了 {total_bookmarks} 个收藏关系")

# ============================================================================
# 最终统计
# ============================================================================
print("\n" + "="*80)
print("真实数据创建完成！最终统计")
print("="*80)

print(f"\n用户: {User.objects.count()} 个")
print(f"  - 拥有Profile: {Profile.objects.count()} 个")

print(f"\n帖子: {Post.objects.count()} 个")
print(f"  - 标签: {Tag.objects.count()} 个")

print(f"\n大学: {University.objects.count()} 个")

print(f"\n交换项目: {ExchangeProgram.objects.count()} 个")
print(f"  - 紧急项目（即将截止）: {ExchangeProgram.objects.filter(is_urgent=True).count()} 个")

print(f"\n实习: {Internship.objects.count()} 个")
print(f"  - 支持远程: {Internship.objects.filter(remote=True).count()} 个")

print(f"\n社区: {Community.objects.count()} 个")
print(f"  - 学习小组: {Community.objects.filter(is_study_group=True).count()} 个")

print(f"\n收藏: {Bookmark.objects.count()} 个")
print(f"  - 帖子收藏: {Bookmark.objects.filter(content_type='post').count()} 个")
print(f"  - 交换项目收藏: {Bookmark.objects.filter(content_type='exchange').count()} 个")
print(f"  - 实习收藏: {Bookmark.objects.filter(content_type='internship').count()} 个")
print(f"  - 社区收藏: {Bookmark.objects.filter(content_type='community').count()} 个")

print("\n" + "="*80)
print("[SUCCESS] 所有真实数据创建完成！")
print("="*80 + "\n")

print("提示：请刷新前端页面查看效果。")
