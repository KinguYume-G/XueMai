<div align="center">

# 🎓 学脉 UniPulse Asia — 全栈开发者文档
### *连接亚太地区大学生的校园社交与学术交流平台*

[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-6%2B-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

**学脉（UniPulse Asia）** 是专为 **Asia Pacific University (APU)** 及亚太地区合作高校学生打造的校园级数字生态平台。系统统一承载「校园动态 Feed」「专业学术论坛」「交换/实习机会发布」「AI 智能学业助手 (Claude RAG)」「实时通知与社交私信」等核心功能。

</div>

---

## 📖 目录 (Table of Contents)

- [🌐 系统概览 (System Overview)](#-系统概览-system-overview)
- [🏗 架构设计 (Architecture)](#-架构设计-architecture)
- [✨ 核心功能特性 (Key Features)](#-核心功能特性-key-features)
- [📂 项目目录结构 (Project Structure)](#-项目目录结构-project-structure)
- [🛠 技术栈清单 (Technology Stack)](#-技术栈清单-technology-stack)
- [🚀 快速启动指南 (Getting Started)](#-快速启动指南-getting-started)
  - [1. 前端配置与启动 (Vite + React)](#1-前端配置与启动-vite--react)
  - [2. 后端配置与启动 (Django DRF)](#2-后端配置与启动-django-drf)
  - [3. 数据库与真实测试数据填充](#3-数据库与真实测试数据填充)
  - [4. Redis 与 Celery 异步服务](#4-redis-与-celery-异步服务)
- [📡 API 规范与文档 (API Reference)](#-api-规范与文档-api-reference)
- [⚙ 环境变量说明 (Environment Variables)](#-环境变量说明-environment-variables)

---

## 🌐 系统概览 (System Overview)

学脉平台通过现代化前端框架与高可拓展后端架构，解决高校学生信息流分散、跨校交流门槛高、实习与交换信息不对称的痛点。

| 模块组件 | 主要技术 | 角色与职责 |
|---|---|---|
| **Web 前端应用** | Vite 5 + React 18 + TypeScript + Zustand + Tailwind CSS | 单页应用 (SPA)，提供极速 UI 响应与交互体验 |
| **Backend REST API** | Django 5.2 + Django REST Framework + SimpleJWT | 核心 API 服务、认证鉴权、权限控制与业务逻辑 |
| **AI 检索增强 (RAG)** | Anthropic Claude LLM + Chroma DB / Supabase pgvector | 课程答疑、校规检索、智能简历解析与创业 BP 指导 |
| **实时通讯与缓存** | Redis 6+ + Python-SocketIO / Celery | 消息通知队列、实时 Push 推送与异步计算 |

---

## 🏗 架构设计 (Architecture)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Frontend (React + Vite)                          │
│ ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐ │
│ │  Feed & Post │  │ Academic     │  │ Opportunities  │  │ AI Assistant   │ │
│ │  Component   │  │ Forums       │  │ (Exchange/Jobs)│  │ Chat Component │ │
│ └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  └───────┬────────┘ │
│        │                 │                  │                   │          │
│        └─────────────────┼──────────────────┴───────────────────┘          │
│                          ▼ (Axios + JWT Auth)                              │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
             ┌─────────────┴──────────────┐
             ▼                            ▼
┌─────────────────────────┐  ┌────────────────────────────────────────────────┐
│   Celery Async Worker   │  │              Django 5.2 Backend                │
│ ┌─────────────────────┐ │  │ ┌────────────┐ ┌──────────────┐ ┌────────────┐ │
│ │ Notification Tasks  │ │  │ │  REST API  │ │ Claude RAG   │ │ JWT Auth   │ │
│ │ RAG Vector Indexing │ │  │ │  Routers   │ │ Orchestrator │ │ Middleware │ │
│ └─────────────────────┘ │  │ └─────┬──────┘ └──────┬───────┘ └────────────┘ │
└────────────┬────────────┘  │       │               │                        │
             │               └───────┼───────────────┼────────────────────────┘
             ▼                       ▼               ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌───────────────────┐
│     Redis 6+ Cache      │  │ PostgreSQL 15 / SQLite  │  │ Chroma DB Vector  │
│ (Celery Broker & State) │  │  (Relational Database)  │  │  (Embedding Store)│
└─────────────────────────┘  └─────────────────────────┘  └───────────────────┘
```

---

## ✨ 核心功能特性 (Key Features)

### 📰 校园动态 (Campus Feed & Posts)
- **多维度 Feed 流**：支持推荐热门 (Hot)、最新发布 (New)、关注好友 (Follow) 动态切换。
- **富文本与富媒体**：支持 Markdown 渲染、图片上传、高亮标签 (Tags)。
- **交互与收藏**：点赞、评论与关联收藏夹。

### 🎓 专业学术论坛 (Academic Forums & Communities)
- **学院与主题分区**：支持按计算机、商业分析、数据科学等专业建立讨论板块。
- **贴子精选与提问**：支持专业问答、置顶精选与交流经验分享。
- **社团与兴趣小组**：社团官方公告发布、活动报名与小组成员互动。

### 💼 交换项目与实习机会 (Exchange & Internships)
- **亚太高校交换项目**：支持新加坡国立大学 (NUS)、南洋理工大学 (NTU)、香港大学 (HKU)、东京大学等交换申请信息展示。
- **名企实习推荐**：直连 Google Malaysia, Grab, Shopee, ByteDance 等名企实习岗位。
- **紧急/热门标注**：自动高亮即将截止的申请项目与热门推荐。

### 🤖 AI 学业助手 (AI Study Companion & RAG)
- **Claude 大语言模型接入**：基于 Anthropic Claude 的智能对话。
- **课程与校规向量检索 (RAG)**：精准解答 APU 课程选课、修业学分与校规细则。
- **多功能 AI 工作流**：
  - 📝 简历解析与修改建议 (Resume Review)
  - 💡 创业商业计划书评估 (BP Evaluator)
  - 💼 模拟面试问答 (Interview Prep)
  - 📊 薪资标准与行情查询 (Salary Benchmarks)

### 🔔 实时消息与社交关系 (Messaging & Notifications)
- **多类型通知**：点赞通知、评论回复通知、关注提醒与系统消息。
- **一键已读**：支持未读计份与批量/全量标记已读。
- **用户关注网络**：粉丝与关注关系追踪。

---

## 📂 项目目录结构 (Project Structure)

```
XueMai/
├── frontend/                          # Vite + React 18 前端应用
│   ├── src/
│   │   ├── main.tsx                   # 应用入口文件
│   │   ├── App.tsx                    # 根路由与 Context
│   │   ├── pages/                     # 页面组件
│   │   │   ├── auth/                  # 登录/注册/重置密码
│   │   │   ├── feed/                  # 动态 Feed 流
│   │   │   ├── forum/                 # 论坛与社区
│   │   │   ├── AIChat/                # AI 对话助手与工作流
│   │   │   ├── apu/                   # APU 专属信息中心
│   │   │   └── messaging/             # 私信与通知面板
│   │   ├── components/                # 通用与业务 UI 组件
│   │   ├── lib/                       # API 客户端与工具集
│   │   ├── services/                  # 服务请求封装
│   │   ├── store/                     # Zustand 状态管理
│   │   ├── types/                     # TypeScript 类型定义
│   │   └── routes/                    # 路由映射表
│   ├── package.json                   # 前端依赖配置
│   └── vite.config.ts                 # Vite 配置文件
│
├── backend/                           # Django 5.2 后端应用
│   ├── config/                        # Django 全局配置中心
│   │   ├── settings/                  # 拆分式配置 (base/dev/prod/test)
│   │   ├── urls.py                    # 根路由配置
│   │   └── asgi.py                    # ASGI 配置 (WebSocket)
│   ├── apps/                          # 业务功能 App
│   │   ├── authentication/            # 认证鉴权模块
│   │   ├── users/                     # 用户 Profile 与关系
│   │   ├── posts/                     # 动态与帖子模块
│   │   ├── comments/                  # 评论与回复
│   │   ├── forums/                    # 专业论坛模块
│   │   ├── communities/               # 社区与社团
│   │   ├── opportunities/             # 交换项目与实习岗位
│   │   ├── ai/                        # AI 智能助手与 RAG 向量引擎
│   │   ├── notifications/             # 通知推送模块
│   │   ├── bookmarks/                 # 收藏夹模块
│   │   └── search/                    # 综合搜索模块
│   ├── scripts/                       # 数据填充与运维脚本
│   ├── manage.py                      # Django 管理脚手架
│   ├── pytest.ini                     # Pytest 配置
│   └── requirements.txt               # 后端依赖列表
│
└── README.md                          # 项目开发者主文档
```

---

## 🛠 技术栈清单 (Technology Stack)

### **前端 (Frontend)**
- **核心框架**：React 18.3 + TypeScript 5.3 + Vite 5.4
- **状态管理**：Zustand 5.0
- **样式与组件**：Tailwind CSS 3.4 + Ant Design 6.0 + Lucide Icons
- **路由与网络**：React Router DOM 6.30 + Axios 1.19
- **代码规范**：ESLint 9.39 + TypeScript-ESLint

### **后端 (Backend)**
- **核心框架**：Django 5.2.7 + Django REST Framework 3.15
- **认证鉴权**：SimpleJWT (JSON Web Token)
- **数据库**：PostgreSQL 15+ (Supabase) / SQLite 3
- **异步与缓存**：Redis 6+ + Celery
- **API 文档**：drf-spectacular (Swagger UI / OpenAPI 3.0)

---

## 🚀 快速启动指南 (Getting Started)

### **前置依赖要求**
- **Node.js** 18.0+
- **pnpm** 8.0+
- **Python** 3.11+
- **Redis** 6.0+ (可选，用于缓存与异步任务)

---

### **1. 前端配置与启动 (Vite + React)**

```powershell
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 运行 TypeScript 类型检查与代码校验
pnpm run lint
pnpm run test

# 启动开发服务器 (监听 http://localhost:3000)
pnpm run dev
```

---

### **2. 后端配置与启动 (Django DRF)**

```powershell
# 进入后端目录
cd backend

# 激活 Python 虚拟环境 (Windows)
.\.venv311\Scripts\activate

# 安装项目依赖
pip install -r requirements.txt

# 运行系统诊断与单元测试 (106 项测试)
python manage.py check
python -m pytest

# 应用数据库迁移
python manage.py migrate

# 启动 Django 本地服务 (监听 http://127.0.0.1:8000)
python manage.py runserver 8000
```

---

### **3. 数据库与真实测试数据填充**

项目自带完备的测试数据生成工具，运行以下指令自动注入真实大学、岗位、帖子与收藏数据：

```powershell
cd backend
cmd /c "set PYTHONIOENCODING=utf-8 && set PYTHONPATH=. && .\.venv311\Scripts\python.exe scripts/create_real_data.py"
```

注入数据包含：
- 🏢 11 所亚太名校（NUS、NTU、HKU、APU 等）
- 👥 18 名已建 Profile 测试用户
- 📝 38 篇图文帖子与 33 个分类标签
- ✈️ 18 个交换项目 & 💼 32 个名企实习岗位
- 👥 7 个专业社团与 162 组关联收藏数据

---

### **4. Redis 与 Celery 异步服务**

```powershell
# 启动 Redis 缓存服务
redis-server

# 启动 Celery Worker 处理后台异步队列
cd backend
celery -A config worker -l info
```

---

## 📡 API 规范与文档 (API Reference)

后端基于 `drf-spectacular` 自动生成完整的 OpenAPI 3.0 规范文档。服务启动后可直接访问：

- **Swagger UI 交互式文档**：[http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **OpenAPI Schema JSON**：[http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### **常用 API 快速览**

| 模块 | 请求方式 | 端点 (Endpoint) | 功能描述 |
|---|---|---|---|
| **认证** | `POST` | `/api/register/` | 用户注册 |
| **认证** | `POST` | `/api/login/` | 用户登录并获取 JWT Token |
| **用户** | `GET` | `/api/users/me/` | 获取当前登录用户 Profile |
| **Feed** | `GET` | `/api/posts/?tab=hot|new|follow` | 分页获取 Feed 流 |
| **Feed** | `POST` | `/api/posts/` | 创建新动态帖子 |
| **机会** | `GET` | `/api/exchange_programs/` | 获取海外交换项目 |
| **机会** | `GET` | `/api/internships/` | 获取实习岗位列表 |
| **AI 助手**| `POST` | `/api/ai/chat/` | Claude RAG 学业智能问答 |
| **通知** | `GET` | `/api/notifications/` | 获取未读消息通知 |

---

## ⚙ 环境变量说明 (Environment Variables)

### 后端配置 (`backend/.env`)
```env
# Django 基础设置
SECRET_KEY=django-insecure-xuemai-secret-key-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库连接 (Supabase PostgreSQL / SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Anthropic Claude API Key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Redis 缓存与 Broker
REDIS_URL=redis://127.0.0.1:6379/0
```

### 前端配置 (`frontend/.env.local`)
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

<div align="center">

**学脉 (UniPulse Asia) — 为亚太高校学子构建的下一代数字校园平台**

</div>