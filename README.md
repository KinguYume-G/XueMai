# 学脉（UniPulse Asia）

学脉是面向高校学生的校园社交与学术资源平台。系统整合校园动态、专业论坛、学生社区、交换项目、实习与创业机会、即时通信以及 AI 学业问答，为学生提供统一的信息获取与交流入口。

项目采用前后端分离架构，由 React 单页应用和 Django REST API 组成。系统使用 JWT 管理用户会话，通过 Django Channels 与 Redis 提供实时通信，使用 Celery 处理异步通知，并集成 Groq、Ollama、LangChain 与 Chroma 实现流式 AI 问答和 RAG 知识检索。

## 功能

- **用户认证**：支持用户注册、登录、JWT 身份认证、会话恢复及个人资料管理。
- **校园动态**：支持帖子发布、信息流浏览、标签分类、评论、点赞、收藏及内容可见范围控制。
- **专业论坛**：按学院和专业组织讨论内容，支持话题发布、论坛统计和热门标签聚合。
- **学生社区**：支持社区创建、社区浏览、成员加入与退出，并维护社区成员统计。
- **学生关系**：支持关注、粉丝、好友申请、联系人列表及用户搜索。
- **即时通信**：支持私信、群组消息、在线状态、最后在线时间、未读统计和消息已读状态。
- **实时事件**：通过 WebSocket 分发聊天消息、在线状态及通知事件，并提供断线重连与 REST 发送回退。
- **通知中心**：为点赞、评论和关注事件创建站内通知，通过 Celery 和 Channels 完成异步处理与实时推送。
- **机会中心**：集中展示交换项目、实习岗位和创业项目，支持搜索、筛选、详情查看及收藏。
- **校园资料**：管理大学、学院和校园资源信息，为论坛、内容和用户资料提供结构化数据。
- **统一收藏**：通过通用收藏模型管理帖子、交换项目、实习及社区等不同类型内容。
- **AI 学业助手**：支持 SSE 流式回答、Groq/Ollama 推理切换、Chroma 向量检索及 RAG 降级处理。
- **接口文档**：使用 drf-spectacular 生成 OpenAPI Schema 和 Swagger UI。
- **媒体上传**：支持本地媒体文件，并可接入 Supabase Storage 管理对象存储。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Frontend | React 18、TypeScript、Vite 5 |
| Routing | React Router |
| State Management | Zustand |
| Data Access | Axios、Fetch API、Server-Sent Events |
| UI | Tailwind CSS、Lucide React |
| Internationalization | i18next、react-i18next |
| Backend | Python、Django 5、Django REST Framework |
| Authentication | Simple JWT |
| Real-time | Django Channels、WebSocket、Redis |
| Async Processing | Celery、Celery Beat |
| Database | PostgreSQL、Django ORM |
| API Documentation | drf-spectacular、OpenAPI、Swagger UI |
| AI | Groq、Ollama |
| RAG | LangChain、Chroma、Ollama Embeddings |
| Storage | Django Media、Supabase Storage |

## 架构

```text
Browser
  -> React + TypeScript 单页应用
  -> React Router 负责页面路由与认证保护
  -> Zustand 管理认证、聊天、收藏及业务状态
  -> Axios Client 处理 REST 请求、JWT 注入和 Token 刷新
  -> SSE 接收 AI 流式响应
  -> WebSocket 接收消息、在线状态和实时通知

Django Application
  -> Django REST Framework 提供领域 API
  -> Simple JWT 负责 Access Token 与 Refresh Token 认证
  -> Django ORM 访问 PostgreSQL
  -> Django Channels 处理 WebSocket 连接与 Channel Group
  -> Redis 提供 Channel Layer、Celery Broker 和任务结果存储
  -> Celery Worker 处理通知创建与实时分发
  -> Celery Beat 执行通知清理等周期任务

AI Pipeline
  -> AI Chat API 接收问题与功能分类
  -> LangChain 组织检索与提示词上下文
  -> Ollama Embeddings 生成查询向量
  -> Chroma 检索相关文档片段
  -> Groq 或 Ollama 生成回答
  -> Server-Sent Events 将结果增量返回前端
```

后端按业务域划分为认证、用户、校园资料、帖子、评论、论坛、社区、社交关系、通知、收藏、机会、上传和 AI 等独立 Django app。各模块分别维护模型、序列化器、视图和路由，公共权限、分页、节流及异常处理由 `backend/core` 统一提供。

用户认证、关系权限、内容可见性、群组成员校验、收藏状态和通知持久化均由应用代码确定。AI 模型仅负责问答生成与知识检索，不参与身份认证、权限控制或核心业务状态判断。
