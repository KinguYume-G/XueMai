# 学脉 UniPulse Asia

面向亚太高校学生的校园社交与学术资源平台。项目将校园动态、专业论坛、学生社区、交换与实习机会、即时消息和 AI 学业助手整合到一个统一入口中。

> **项目状态：作品集归档。** 核心功能和数据模型已实现；原远程数据库与第三方服务已停用。重新运行项目前，需要自行配置数据库及可选的 AI、Redis 和对象存储服务。

## 项目亮点

- **前后端分离架构**：React + TypeScript 单页应用，对接 Django REST Framework API。
- **校园社交领域建模**：覆盖帖子、评论、标签、收藏、关注、好友、私信、群组、通知和社区。
- **机会信息聚合**：统一管理交换项目、实习和创业项目，支持筛选、搜索和排序。
- **AI 学业助手**：支持 SSE 流式回答、Groq/Ollama 模型回退和 Chroma RAG 检索流程。
- **统一身份与请求层**：JWT 登录、Token 自动刷新、路由守卫和集中式 Axios 错误处理。
- **国际化基础**：通过 i18next 管理中英文界面文案。

## 功能概览

| 模块 | 已实现能力 |
|---|---|
| 身份认证 | 注册、登录、JWT、会话恢复、个人资料 |
| 校园动态 | Feed、帖子、标签、评论、点赞、收藏 |
| 论坛与社区 | 学院分类、论坛话题、社区、加入与退出 |
| 机会中心 | 交换项目、实习、创业项目、筛选与搜索 |
| 社交关系 | 关注、粉丝、好友申请、联系人搜索 |
| 消息系统 | 私信、群组、未读统计、已读状态 |
| 通知中心 | 点赞、评论、关注及系统通知 |
| 校园资料 | 大学、学院和校园资源 |
| AI 助手 | SSE 流式对话、Groq/Ollama、Chroma RAG |
| 媒体上传 | 图片/视频校验、Supabase 预签名地址 |

部分发布入口和 AI 工具卡片仍为 Coming Soon，用于体现产品规划边界，不应被视为已交付功能。

## 技术栈

### 前端

- React 18、TypeScript、Vite 5
- React Router、Zustand、Axios
- Tailwind CSS、Lucide React
- i18next、React Markdown

### 后端

- Python、Django 5、Django REST Framework
- Simple JWT、django-filter、drf-spectacular
- PostgreSQL 或本地 SQLite
- Celery、Redis、Django Channels（扩展依赖）
- Supabase Storage（可选）

### AI / RAG

- Groq API：首选远程推理服务
- Ollama：本地模型回退
- LangChain、Chroma：文档切分和向量检索
- Server-Sent Events：流式输出

## 系统架构

```text
React SPA
  ├─ Router + Auth Guard
  ├─ Zustand Stores
  └─ Axios API Client
          │ JWT / JSON
          ▼
Django REST API
  ├─ Authentication / Users / Campus
  ├─ Posts / Comments / Forums / Communities
  ├─ Social / Chat / Notifications / Bookmarks
  ├─ Opportunities / Uploads
  └─ AI API ──> Groq or Ollama ──> Chroma RAG
          │
          ▼
 PostgreSQL / SQLite
```

当前聊天功能通过 REST API 工作。仓库保留 Channels、Socket.IO 和 Redis 相关依赖，但 WebSocket consumer 尚未接入 ASGI 路由。

## 目录结构

```text
.
├── frontend/
│   ├── public/                 # 静态资源
│   └── src/
│       ├── components/         # 布局、业务和 UI 组件
│       ├── hooks/              # AI 流式请求等复用逻辑
│       ├── i18n/               # 中英文文案
│       ├── lib/                # Axios、Token 和通用工具
│       ├── pages/              # 页面级组件
│       ├── routes/             # 路由和应用布局
│       ├── services/api/       # 后端 API 访问层
│       ├── store/              # Zustand 状态
│       └── types/              # TypeScript 类型
├── backend/
│   ├── apps/                   # Django 业务应用
│   ├── config/                 # Settings、URL、ASGI、WSGI、Celery
│   ├── core/                   # 权限、分页、节流和异常处理
│   ├── manage.py
│   ├── requirements.txt
│   └── requirements-ai.txt
└── README.md
```

## 核心数据模型

```text
User ── Profile ── University / School
  ├── Post ── Comment / Like / Tag / Bookmark
  ├── Follow / FriendRequest
  ├── ChatGroup / ChatMessage
  ├── Notification
  ├── CommunityMember ── Community
  ├── Topic ── Forum
  └── ExchangeProgram / Internship / Startup

AIDocument ── AIChunk ── AIEmbedding
User ── AIQueryLog
```

## 本地运行

### 前置条件

- Node.js 18+
- pnpm
- Python 3.11+
- PostgreSQL（可选；不设置时使用 SQLite）
- Redis、Ollama、Groq 和 Supabase 均为可选服务

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-ai.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

后端默认地址为 `http://127.0.0.1:8000`，API 文档位于 `http://127.0.0.1:8000/api/docs/`。

AI 第三方 SDK 可能随生态版本变化，长期归档后重新启用时应再次锁定和验证。Supabase 上传是可选能力，如需启用还应安装对应 Python SDK。

### 2. 前端

```bash
cd frontend
pnpm install
cp .env.example .env.local
pnpm dev
```

前端默认地址为 `http://localhost:3000`。

## 环境变量

仓库只提交不含凭据的 `.env.example`。真实 `.env` 和 `.env.local` 不应提交到 Git。

### 后端

| 变量 | 用途 |
|---|---|
| `SECRET_KEY` | Django 签名密钥 |
| `DEBUG` | 是否启用开发模式 |
| `ALLOWED_HOSTS` | 允许访问的 Host 列表 |
| `DATABASE_URL` | 数据库连接；可使用 SQLite URL |
| `GROQ_API_KEY` | 可选的 Groq AI 推理 |
| `REDIS_URL` | 可选的 Celery Broker/Result Backend |
| `SUPABASE_URL` | 可选的 Supabase 项目地址 |
| `SUPABASE_SERVICE_ROLE_KEY` | 服务端存储凭据，严禁暴露给前端 |
| `SUPABASE_BUCKET` | 上传存储桶名称 |

### 前端

| 变量 | 用途 |
|---|---|
| `VITE_API_BASE_URL` | Django API 根地址，例如 `http://127.0.0.1:8000/api` |

## 主要 API

| 范围 | 路径示例 |
|---|---|
| 认证 | `/api/auth/register/`、`/api/auth/login/`、`/api/auth/me/` |
| 帖子 | `/api/posts/`、`/api/feed/`、`/api/comments/`、`/api/tags/` |
| 校园 | `/api/universities/`、`/api/schools/` |
| 社交与聊天 | `/api/follow/`、`/api/follows/`、`/api/chat/*` |
| 通知 | `/api/notifications/` |
| 收藏 | `/api/bookmarks/` |
| 论坛和社区 | `/api/forums/`、`/api/topics/`、`/api/communities/` |
| 机会 | `/api/exchange_programs/`、`/api/internships/`、`/api/startups/` |
| AI | `/api/ai/chat/stream/`、`/api/ai/chat/sync/`、`/api/ai/health/` |
| OpenAPI | `/api/schema/`、`/api/docs/` |

## 工程质量命令

```bash
cd frontend
pnpm lint                       # ESLint
pnpm build                      # TypeScript + Vite build

cd ../backend
python manage.py check          # Django configuration check
python manage.py test           # Django tests
```

后端命令需要已安装依赖和有效环境配置。本归档没有附带原线上数据库。

## 已知边界

- 原线上数据库和第三方服务已停用，仓库不包含真实数据或凭据。
- 数据迁移保留，以展示数据模型演进；重新部署时应在新数据库执行。
- AI/RAG 依赖本地 Ollama 或有效 Groq 配置，仓库不附带模型及生成的向量索引。
- Channels、Celery 和 Redis 已预留基础配置，但尚未形成完整实时消息和异步任务链路。
- 部分机会收藏统计、论坛热度和在线状态仍为 TODO 或演示实现。
- 当前没有持续集成配置；完整运行验证需要重新配置开发环境。

## 项目背景

该项目用于探索高校场景下的全栈产品设计：如何将身份、内容、关系链、机会信息和 AI 检索能力组织为一套可扩展的校园平台。代码重点展示领域拆分、REST API 设计、前端状态管理、JWT 会话处理和 RAG 工作流，而不是提供仍在运营的线上服务。

## License

本项目当前未声明开源许可证。未经作者许可，不得将代码用于再发布或商业用途。
