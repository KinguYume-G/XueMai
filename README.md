# 学脉 · UniPulse Asia

面向高校学生的校园社交与学术资源平台。

学脉将校园内容、专业讨论、学生社区、交换与实习机会、站内消息和学业问答集中在同一套产品中。项目采用 React 与 Django REST Framework 构建，覆盖从前端交互、状态管理和身份认证，到关系型数据建模、REST API 与 RAG 问答的完整链路。

## 功能

### 校园内容

- 发布和浏览校园动态
- 帖子标签、评论、点赞与收藏
- 按最新、热门和关注关系组织 Feed
- 学院论坛、话题分类与社区

### 学生关系

- 关注、粉丝和好友申请
- 联系人搜索、私信与群组消息
- 未读消息统计和已读状态
- 点赞、评论、关注及系统通知

### 机会与资源

- 交换项目、实习岗位和创业项目
- 按学校、地区、类型和截止日期筛选
- 大学、学院及校园资源信息
- 多内容类型统一收藏

### AI 学业助手

- 基于 Server-Sent Events 的流式回答
- Groq 与本地 Ollama 两种推理方式
- 使用 LangChain 和 Chroma 完成文档切分、向量检索与上下文组装
- RAG 不可用时退回普通对话，避免检索服务影响基本问答

## 技术架构

```text
┌─────────────────────────────────────────────────────┐
│                    React Client                     │
│  Router · Auth Guard · Zustand · Axios · i18next   │
└──────────────────────────┬──────────────────────────┘
                           │ JSON / JWT / SSE / WebSocket
┌──────────────────────────▼──────────────────────────┐
│                    Django REST API                  │
│                                                     │
│  Auth      Content      Social       Opportunities  │
│  Campus    Forums       Messages     Notifications  │
│  Uploads   Bookmarks    OpenAPI      AI Assistant   │
└───────────────┬─────────────────────────┬───────────┘
                │                         │
┌───────────────▼──────────────┐  ┌───────▼───────────┐
│     PostgreSQL / SQLite      │  │ Groq / Ollama     │
│   Django ORM · Migrations    │  │ LangChain · Chroma│
└──────────────────────────────┘  └───────────────────┘
```

### 前端

| 范围 | 实现 |
|---|---|
| 应用框架 | React 18、TypeScript、Vite 5 |
| 路由 | React Router，受保护路由统一处理登录状态 |
| 状态 | Zustand 管理认证、聊天、收藏与机会页面状态 |
| 网络层 | Axios 实例统一处理 API 地址、JWT 注入、Token 刷新和错误响应 |
| 样式 | Tailwind CSS 与可复用 UI 组件 |
| 国际化 | i18next、react-i18next |
| AI 输出 | Fetch + SSE 增量解析 |

### 后端

| 范围 | 实现 |
|---|---|
| API | Django 5、Django REST Framework |
| 认证 | Simple JWT，Access/Refresh Token 轮换 |
| 数据访问 | Django ORM、过滤、搜索、排序和分页 |
| 接口文档 | drf-spectacular 生成 OpenAPI Schema 与 Swagger UI |
| 文件存储 | 本地媒体目录；可选 Supabase Storage |
| 实时通信 | Django Channels、Redis Channel Layer、JWT WebSocket |
| 异步任务 | Celery 处理通知创建、实时分发和过期数据清理 |
| AI/RAG | Groq、Ollama、LangChain、Chroma |

## 关键实现

### JWT 会话管理

前端通过共享 Axios Client 发送请求。请求拦截器自动附加 Access Token；接口返回 `401` 时，客户端只发起一次 Refresh 请求，并让并发失败请求等待同一个刷新结果。刷新失败后统一清理本地会话并返回登录页。

### 实时消息与在线状态

登录用户通过 JWT 建立 WebSocket 连接。Channels Consumer 将连接加入用户和群组 Channel Group，负责私信、群聊、通知和在线状态事件。REST 消息接口与 WebSocket 使用同一套序列化结构，因此断线时仍可通过 HTTP 完成发送，连接恢复后继续接收实时事件。

用户连接和断开时会更新现有 `UserOnlineStatus` 记录；前端同步更新联系人列表与会话标题中的在线状态和最后在线时间。

### 异步通知

点赞、评论和关注事件通过 Django Signals 触发，并在数据库事务提交后交给 Celery。Worker 创建通知后，将事件发送到对应用户的 Channel Group。Celery Beat 每日清理超过保留期限的已读通知。

### 领域拆分

后端按业务域拆分 Django app，而不是把所有接口集中在单一模块中：

```text
authentication   注册、登录和当前用户
users            用户与扩展资料
campus           大学、学院和校园资源
posts            帖子、标签、点赞和 Feed
comments         评论与回复
forums           学院论坛和话题
communities      学生社区与成员关系
social           关注、好友、聊天和群组
notifications    站内通知与未读状态
bookmarks        跨内容类型收藏
opportunities    交换、实习和创业项目
uploads          媒体上传地址
ai               流式问答与 RAG
```

各模块分别维护模型、序列化器、视图、路由和迁移，公共权限、分页、节流与异常处理位于 `backend/core`。

### 数据关系

```text
User ──1:1── Profile ──> University / School
  │
  ├── Post ──> Comment / Tag / PostLike
  ├── Follow / FriendRequest
  ├── ChatGroup / ChatMessage
  ├── Notification
  ├── CommunityMember ──> Community
  ├── Topic ──> Forum
  └── ExchangeProgram / Internship / Startup

AIDocument ──> AIChunk ──1:1── AIEmbedding
User ──> AIQueryLog
```

### RAG 请求流程

1. 前端向流式聊天接口提交问题。
2. 后端使用 Ollama Embeddings 将问题向量化。
3. Chroma 返回相关文档片段。
4. 检索结果与学业助手 System Prompt 一起组成模型上下文。
5. Groq 或 Ollama 生成回答，并通过 SSE 持续返回前端。
6. 检索失败时记录异常并继续普通对话。

## 项目结构

```text
.
├── frontend/
│   ├── public/                 # 图片与静态资源
│   └── src/
│       ├── components/         # 业务组件、布局和基础 UI
│       ├── hooks/              # 可复用交互逻辑
│       ├── i18n/               # 中英文资源
│       ├── lib/                # API Client、Token 与通用工具
│       ├── pages/              # 页面组件
│       ├── routes/             # 路由与应用布局
│       ├── services/api/       # API 服务层
│       ├── store/              # Zustand Store
│       └── types/              # TypeScript 类型
├── backend/
│   ├── apps/                   # Django 业务模块
│   ├── config/                 # Settings、URL、ASGI、WSGI、Celery
│   ├── core/                   # 权限、分页、节流和异常处理
│   ├── manage.py
│   ├── requirements.txt
│   └── requirements-ai.txt
└── README.md
```

## 本地开发

### 环境要求

- Node.js 18+
- pnpm
- Python 3.11+
- PostgreSQL
- Redis（实时消息、在线状态和异步通知）

Ollama、Groq 和 Supabase 仅在使用对应功能时需要。

### 后端

```bash
cd backend

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt -r requirements-ai.txt
cp .env.example .env

python manage.py migrate
python manage.py runserver
```

服务启动后：

- API：`http://127.0.0.1:8000/api/`
- Swagger UI：`http://127.0.0.1:8000/api/docs/`
- OpenAPI Schema：`http://127.0.0.1:8000/api/schema/`

实时消息和异步通知还需要启动 Celery Worker 与 Beat：

```bash
celery -A config worker -l info
celery -A config beat -l info
```

### 前端

```bash
cd frontend

pnpm install
cp .env.example .env.local
pnpm dev
```

前端默认运行在 `http://localhost:3000`。

## 配置

### 后端环境变量

| 变量 | 必需 | 说明 |
|---|:---:|---|
| `SECRET_KEY` | 是 | Django 签名密钥 |
| `DEBUG` | 否 | 默认为 `False`；开发环境可设为 `True` |
| `ALLOWED_HOSTS` | 否 | 以逗号分隔的 Host 列表 |
| `DATABASE_URL` | 否 | 未配置时使用本地 SQLite |
| `GROQ_API_KEY` | 否 | 启用 Groq 推理 |
| `REDIS_URL` | 实时功能必需 | Channels、Celery Broker 与 Result Backend |
| `CELERY_BROKER_URL` | 否 | 单独指定 Celery Broker |
| `CELERY_RESULT_BACKEND` | 否 | 单独指定结果存储 |
| `SUPABASE_URL` | 否 | Supabase 项目地址 |
| `SUPABASE_SERVICE_ROLE_KEY` | 否 | 服务端存储凭据，不得传入前端 |
| `SUPABASE_BUCKET` | 否 | 媒体文件 Bucket，默认 `uploads` |

### 前端环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000/api` | Django API 根地址 |

示例配置位于 `backend/.env.example` 和 `frontend/.env.example`。实际环境文件已通过 `.gitignore` 排除。

## API 概览

| 业务域 | Endpoint |
|---|---|
| Authentication | `/api/auth/register/`、`/api/auth/login/`、`/api/auth/me/` |
| Users & Campus | `/api/users/`、`/api/profiles/`、`/api/universities/`、`/api/schools/` |
| Content | `/api/posts/`、`/api/feed/`、`/api/comments/`、`/api/tags/` |
| Forums & Communities | `/api/forums/`、`/api/topics/`、`/api/communities/` |
| Social & Chat | `/api/follow/`、`/api/follows/`、`/api/chat/*` |
| Notifications | `/api/notifications/` |
| Bookmarks | `/api/bookmarks/` |
| Opportunities | `/api/exchange_programs/`、`/api/internships/`、`/api/startups/` |
| AI | `/api/ai/chat/stream/`、`/api/ai/chat/sync/`、`/api/ai/health/` |

WebSocket 入口为 `/ws/chat/?token=<access-token>`，用于消息、在线状态和通知事件。

具体请求参数、响应结构和可用操作以 Swagger UI 生成的接口文档为准。

## 代码检查

```bash
# Frontend
cd frontend
pnpm lint
pnpm build

# Backend
cd backend
python manage.py check
python manage.py test
```

## 当前状态

这个仓库保留的是项目开发完成时的代码快照。原远程数据库和第三方服务实例已停止，因此仓库不附带可用的线上数据、模型文件、向量索引或服务凭据。若要重新部署，需要创建新的数据库并重新配置相关服务。

帖子、论坛话题、社区和职位发布入口均已接入对应 API；论坛统计与热门标签来自数据库聚合，交换和实习机会使用统一收藏模型。实时消息、在线状态和通知依赖 Redis、Channels 与 Celery，重新部署时需要同时恢复这些服务。

## License

本项目未声明开源许可证。代码版权归项目作者所有。
