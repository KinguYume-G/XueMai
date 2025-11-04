# 学脉 | UniPulse Asia - MVP 变更清单

## 🎉 已完成功能

### 后端（Django + DRF）

#### 1. 基础设施
- ✅ 更新 `requirements.txt`，添加所有必需依赖
- ✅ 配置 `config/settings/base.py`
  - 数据库配置（支持Supabase PostgreSQL和SQLite）
  - REST Framework配置（认证、分页、过滤）
  - JWT配置（24小时access token，7天refresh token）
  - CORS配置（支持localhost:3000）
  - 自定义User模型配置
- ✅ 更新 `config/urls.py`，汇总所有API路由

#### 2. 应用模块

##### apps/campus（校园管理）
- ✅ `University` 模型：大学信息
- ✅ `School` 模型：学院信息
- ✅ 完整的序列化器、视图集、URL路由
- ✅ 只读API（GET），支持搜索和过滤

##### apps/users（用户系统）
- ✅ 自定义 `User` 模型（继承AbstractUser）
- ✅ `Profile` 模型：用户扩展资料
- ✅ 自动创建Profile信号
- ✅ 用户和资料的完整CRUD API
- ✅ `/api/profiles/me/` - 获取当前用户资料
- ✅ `/api/profiles/update_me/` - 更新当前用户资料

##### apps/posts（帖子系统）
- ✅ `Post` 模型：帖子内容和统计
- ✅ `Tag` 模型：标签系统
- ✅ `PostLike` 模型：点赞功能
- ✅ `Bookmark` 模型：收藏功能
- ✅ `Visibility` 枚举：4种可见性级别（PUBLIC, FOLLOWERS, UNIVERSITY, PRIVATE）
- ✅ `PostQuerySet.visible_to(user)` 方法：智能可见性过滤
- ✅ 完整的帖子CRUD API
- ✅ 点赞/取消点赞API
- ✅ 收藏/取消收藏API
- ✅ 我的收藏列表API

##### apps/comments（评论系统）
- ✅ `Comment` 模型：支持楼中楼（嵌套评论）
- ✅ 父评论和回复关系
- ✅ 创建评论时自动更新帖子评论数
- ✅ 支持查询帖子的所有评论（含回复）

##### apps/social（社交网络）
- ✅ `Follow` 模型：关注关系
- ✅ 防止自己关注自己
- ✅ 自动更新双方的关注/粉丝计数
- ✅ 关注/取消关注API
- ✅ 我关注的人列表
- ✅ 我的粉丝列表

##### apps/notifications（通知系统）
- ✅ `Notification` 模型：6种通知类型
- ✅ 帖子被点赞 → 通知作者
- ✅ 帖子被评论 → 通知作者
- ✅ 评论被回复 → 通知原评论者
- ✅ 被关注 → 通知被关注者
- ✅ 未读通知数API
- ✅ 标记已读/全部已读API
- ✅ 清空已读通知API

##### apps/opportunities（机会发布）
- ✅ `ExchangeProgram` 模型：交换项目
- ✅ `Internship` 模型：实习机会
- ✅ 完整的CRUD API
- ✅ 浏览量统计
- ✅ 支持搜索、过滤、排序

#### 3. 管理和工具
- ✅ 所有模型注册到Django Admin
- ✅ `seed_mvp` 管理命令：生成测试数据
  - 5所大学，15个学院
  - 10个测试用户
  - 50个帖子，多个标签
  - 关注关系、点赞、评论、收藏
  - 10个交换项目，15个实习
- ✅ `test_db_connection.py`：测试数据库连接

#### 4. API文档
- ✅ drf-spectacular集成
- ✅ Swagger UI：`/api/docs/`
- ✅ OpenAPI Schema：`/api/schema/`

---

### 前端（React + TypeScript）

#### 1. API客户端
- ✅ `axios.ts`：配置axios实例
  - 自动附加JWT token
  - 自动刷新过期token
  - 401错误处理
- ✅ `auth.ts`：认证API
  - 登录、登出、刷新token
- ✅ `posts.ts`：帖子API
  - 获取、创建、更新、删除帖子
  - 点赞、收藏功能
- ✅ `users.ts`：用户API
  - 获取当前用户
  - 获取和更新资料
- ✅ `comments.ts`：评论API
- ✅ `social.ts`：社交API
- ✅ `notifications.ts`：通知API

#### 2. TypeScript类型
- ✅ `types/api.ts`：完整的类型定义
  - User, Profile
  - Post, Tag, Comment
  - Follow, Notification
  - University, School
  - ExchangeProgram, Internship
  - PaginatedResponse 泛型

---

### 配置和文档

- ✅ `backend/.env.example`：环境变量示例
- ✅ `frontend/.env.local.example`：前端环境变量示例
- ✅ `RUN_NOTES.md`：完整的运行文档
- ✅ `CHANGELOG.md`：变更清单（本文件）

---

## 📦 生成的文件清单

### 后端（Backend）
```
backend/
├── requirements.txt                      # 更新
├── config/
│   ├── settings/base.py                 # 更新
│   └── urls.py                          # 更新
├── apps/
│   ├── campus/                          # 新建
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── users/                           # 更新
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # 添加Profile模型
│   │   ├── signals.py                   # 新建
│   │   ├── admin.py                     # 更新
│   │   ├── serializers.py               # 更新
│   │   ├── views.py                     # 更新
│   │   └── urls.py                      # 更新
│   ├── posts/                           # 更新
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # 完整实现
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── comments/                        # 新建
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── social/                          # 新建
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── notifications/                   # 新建
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── opportunities/                   # 新建
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       ├── admin.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── core/
│   └── management/
│       └── commands/
│           ├── __init__.py              # 新建
│           └── seed_mvp.py              # 新建
├── .env.example                         # 新建
└── test_db_connection.py                # 新建
```

### 前端（Frontend）
```
frontend/
├── src/
│   ├── services/
│   │   └── api/                         # 新建
│   │       ├── axios.ts
│   │       ├── auth.ts
│   │       ├── posts.ts
│   │       ├── users.ts
│   │       ├── comments.ts
│   │       ├── social.ts
│   │       ├── notifications.ts
│   │       └── index.ts
│   └── types/
│       └── api.ts                       # 新建
└── .env.local.example                   # 新建（被globalIgnore阻止）
```

### 根目录
```
├── RUN_NOTES.md                          # 新建
└── CHANGELOG.md                          # 新建
```

---

## 🚀 快速启动命令

### 后端
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_mvp
python manage.py runserver
```

### 前端
```bash
cd frontend
pnpm install
# 手动创建 .env.local 文件并添加：VITE_API_BASE_URL=http://localhost:8000/api
pnpm dev
```

---

## 📊 数据统计

- **后端应用数量**：7个（campus, users, posts, comments, social, notifications, opportunities）
- **数据模型总数**：13个
- **API端点数量**：50+
- **前端API客户端**：6个模块
- **TypeScript类型定义**：15+

---

## 🎯 核心特性

### 1. 智能可见性控制
- 4种可见性级别
- 自动过滤用户可见内容
- 基于关注关系和大学的访问控制

### 2. 完整的社交功能
- 关注/粉丝系统
- 自动更新统计计数
- 防止自己关注自己

### 3. 实时通知
- 6种通知类型
- 自动触发通知
- 未读通知计数

### 4. 楼中楼评论
- 支持嵌套评论
- 父评论和回复关系
- 自动更新评论数

### 5. JWT认证
- 自动token刷新
- 安全的API访问
- 前端自动处理token

---

## 🔐 测试账号

| 用户名 | 密码 | 用途 |
|--------|------|------|
| alice | testpass123 | 测试用户1 |
| bob | testpass123 | 测试用户2 |
| charlie | testpass123 | 测试用户3 |

运行 `python manage.py seed_mvp` 生成更多测试数据。

---

## 📝 下一步计划

### 短期（MVP+）
- [ ] 前端UI实现
- [ ] 搜索功能优化
- [ ] 图片上传（整合S3/OSS）
- [ ] 邮件通知

### 中期
- [ ] WebSocket实时通知
- [ ] 消息聊天系统
- [ ] 活动管理
- [ ] 问答模块

### 长期
- [ ] AI内容推荐
- [ ] 数据分析仪表板
- [ ] 移动端应用
- [ ] 国际化（i18n）

---

## 🙏 致谢

感谢使用学脉（UniPulse Asia）！本MVP为完整功能的后端API和前端对接奠定了坚实基础。

---

**最后更新**：2025年10月28日

