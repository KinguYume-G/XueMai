、# 学脉 UniPulse Asia - 完整开发者文档

> 连接亚太地区大学生的校园社交与学术交流平台 | Vite + React + TypeScript + Django + PostgreSQL

---

## 🎯 项目定位

**学脉（UniPulse Asia）** 是为 APU 与亚太地区合作高校学生打造的校园级数字平台，统一承载「校园动态」「专业论坛」「交换/实习信息」「AI 学业助手」「实时消息」等能力，解决信息流分散、跨校协作困难、资源不集中的痛点。

### **核心目标**
- 给学生一个能「发、看、问、找人、做项目、问 AI」的入口
- 给学校/社团一个可以「发公告、收报名、招志愿者」的入口
- 给企业/HR 一个可以「直接面向高校学生发岗位」的入口
- 给开发者一个「能在 Cursor 里继续生成代码」的清晰骨架

---

## 🛠️ 技术栈

### **前端**
```
Framework:  Vite 5 + React 18
Language:   TypeScript (严格模式)
Styling:    Tailwind CSS + shadcn/ui
State:      Zustand
Router:     react-router-dom
HTTP:       Axios
Real-time:  socket.io-client
Forms:      React Hook Form + Zod
```

### **后端**
```
Framework:  Django 5.2.7
API:        Django REST Framework 3.15.2
Auth:       djangorestframework-simplejwt (JWT)
Database:   PostgreSQL 15+ (Supabase)
Cache:      Redis
Storage:    Supabase Storage / Cloudflare R2
Tasks:      Celery + Redis
Real-time:  python-socketio / Django Channels
Docs:       drf-spectacular (OpenAPI/Swagger)
```

### **AI & 向量检索**
```
LLM:        Anthropic Claude (主要对话模型)
Vectors:    Supabase pgvector / Pinecone
Embedding:  OpenAI Embeddings / 本地向量化
RAG:        课程、校规、公告向量化检索
```

---

## 🚀 快速启动

### **前置要求**
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 6+

### **1. 克隆项目**
```bash
git clone <repository-url>
cd xuemai-platform
```

### **2. 启动后端**
```powershell
cd backend
.venv\Scripts\activate 
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env）
python manage.py migrate
python manage.py seed_full_data --clear
python manage.py runserver
```
**后端地址：** http://127.0.0.1:8000

### **3. 启动前端**
```powershell
cd frontend
pnpm install
pnpm dev


# 配置环境变量（复制 .env.example 为 .env.local）
它的目标就是把现在的几个点一次性修完：① /login 无限渲染；② 注册第二步字段名/路径不对；③ 所有请求都走同一个 axios client；④ 能自己写出验证步骤。
```
**前端地址：** http://localhost:3000

### **4. 启动 Redis（可选，用于 Celery 和缓存）**
```powershell
redis-server
```

### **5. 启动 Celery Worker（可选，用于异步任务）**
```powershell
cd backend
celery -A config worker -l info
```

---

## 📂 项目结构
```
xuemai-platform/
├── frontend/                          # Vite + React 前端
│   ├── src/
│   │   ├── main.tsx                   # Vite 入口
│   │   ├── App.tsx                    # 根组件
│   │   ├── pages/                     # 页面组件
│   │   │   ├── auth/                  # 认证页面
│   │   │   ├── feed/                  # Feed 流
│   │   │   ├── forum/                 # 论坛
│   │   │   ├── ai/                    # AI 助手
│   │   │   ├── apu/                   # APU 信息中心
│   │   │   └── messaging/             # 私信
│   │   ├── components/                # UI 组件
│   │   │   ├── auth/                  # 认证组件
│   │   │   ├── layout/                # 布局组件
│   │   │   ├── feed/                  # Feed 组件
│   │   │   ├── forum/                 # 论坛组件
│   │   │   ├── ai/                    # AI 组件
│   │   │   ├── notification/          # 通知组件
│   │   │   └── common/                # 通用组件
│   │   ├── lib/                       # 工具库
│   │   │   ├── api/                   # API 客户端
│   │   │   ├── auth/                  # 认证工具
│   │   │   └── websocket/             # WebSocket 管理
│   │   ├── services/                  # API 服务层
│   │   │   └── api/
│   │   ├── store/                     # Zustand 状态
│   │   ├── types/                     # TypeScript 类型
│   │   ├── hooks/                     # 自定义 Hooks
│   │   └── routes/                    # 路由配置
│   ├── .env.example                   # 环境变量模板
│   └── vite.config.ts
│
├── backend/                           # Django 后端
│   ├── config/                        # Django 配置
│   │   ├── settings/
│   │   │   ├── base.py                # 基础配置
│   │   │   ├── development.py         # 开发配置
│   │   │   └── production.py          # 生产配置
│   │   ├── urls.py                    # 主路由
│   │   ├── wsgi.py                    # WSGI 配置
│   │   └── asgi.py                    # ASGI 配置（WebSocket）
│   ├── apps/                          # Django 应用
│   │   ├── accounts/                  # 用户、认证、Profile
│   │   ├── posts/                     # 帖子、Feed、点赞、收藏
│   │   ├── comments/                  # 评论、回复
│   │   ├── forums/                    # 论坛、话题、分区
│   │   ├── social/                    # 关注、粉丝
│   │   ├── notifications/             # 通知系统
│   │   ├── ai_assistant/              # AI 助手、RAG
│   │   ├── apu_hub/                   # APU 信息中心
│   │   ├── messaging/                 # 私信、群聊
│   │   ├── opportunities/             # 交换项目、实习
│   │   └── media/                     # 媒体上传
│   ├── core/                          # 核心工具
│   │   ├── permissions.py             # 权限类
│   │   ├── pagination.py              # 分页类
│   │   └── utils.py                   # 工具函数
│   ├── requirements/
│   │   ├── base.txt                   # 基础依赖
│   │   ├── development.txt            # 开发依赖
│   │   └── production.txt             # 生产依赖
│   ├── .env.example                   # 环境变量模板
│   └── manage.py
│
├── docs/                              # 文档
│   ├── API_DOCUMENTATION.md           # API 完整文档
│   ├── DEPLOYMENT_GUIDE.md            # 部署指南
│   ├── DEVELOPMENT_GUIDE.md           # 开发指南
│   ├── ARCHITECTURE.md                # 架构设计
│   └── UI_DESIGN.md                   # UI 规范
│
└── README.md                          # 本文件
```

---

## 📡 核心功能模块

### **1. 用户与身份（accounts）**
- ✅ 邮箱/校邮注册与登录
- ✅ JWT Token 认证
- ✅ 用户资料（头像、学校、专业、年级、bio）
- ✅ 关注/粉丝系统
- 🔄 隐私设置（计划中）

### **2. 社交 Feed（posts）**
- ✅ 图文发帖
- ✅ 点赞、评论、收藏
- ✅ 按时间/热门/关注查看
- ✅ 标签系统
- 🔄 举报与内容审核（计划中）

### **3. 专业论坛（forums）**
- 🔄 按学科/学院/话题分区
- 🔄 发主题帖、回复、楼中楼
- 🔄 匿名提问模式
- 🔄 精选与置顶

### **4. APU 信息中心（apu_hub）**
- 🔄 课程信息、选课说明
- ✅ 实习与交换项目
- 🔄 导师/社团/校内资源
- 🔄 APU 邮箱认证内容

### **5. AI 助手（ai_assistant）**
- 🔄 学业问答（RAG）
- 🔄 职业增强（简历检查、模拟面试）
- 🔄 翻译/润色
- 🔄 创业场景（BP 框架）

### **6. 实时消息（messaging）**
- ✅ 通知系统（点赞、评论、关注）
- 🔄 私信/群聊
- 🔄 WebSocket 实时推送
- 🔄 在线状态

### **7. 搜索与发现**
- 🔄 搜人、搜帖子、搜论坛
- 🔄 热门话题
- 🔄 推荐用户

**图例：** ✅ 已完成 | 🔄 开发中 | 📋 计划中

---

## 📋 API 端点

### **认证（/api/auth/）**
```
POST   /register/           注册（只需 username/email/password）
POST   /login/              登录
GET    /me/                 当前用户信息
POST   /token/refresh/      刷新 Token
```

### **Feed（/api/feed/）**
```
GET    /?tab=hot|new|follow Feed 流（三种模式）
POST   /posts/              发帖
POST   /posts/{id}/like/    点赞（幂等）
POST   /posts/{id}/bookmark/ 收藏（幂等）
GET    /posts/{id}/         帖子详情
```

### **社交（/api/）**
```
POST   /users/{id}/follow/  关注（幂等）
GET    /following/          关注列表
GET    /followers/          粉丝列表
```

### **评论（/api/comments/）**
```
GET    /?post_id={id}       评论列表
POST   /                    发表评论
```

### **通知（/api/notifications/）**
```
GET    /                    通知列表（含未读数）
POST   /read/               批量已读
POST   /read_all/           全部已读
```

### **交换/实习（/api/）**
```
GET    /exchange_programs/  交换项目列表
GET    /internships/        实习机会列表
```

### **文档**
```
GET    /api/docs/           Swagger UI
GET    /api/schema/         OpenAPI Schema
```

---

## ⚙️ 环境变量

### **后端 `.env`**
```env
# Django 配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库（Supabase PostgreSQL）
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Redis（Celery + 缓存）
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # 分钟
JWT_REFRESH_TOKEN_LIFETIME=7  # 天

# Supabase 存储（后端使用 service_role key）
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Cloudflare R2（可选，替代 Supabase Storage）
AWS_ACCESS_KEY_ID=your-r2-access-key
AWS_SECRET_ACCESS_KEY=your-r2-secret-key
AWS_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
AWS_STORAGE_BUCKET_NAME=xuemai-media

# AI 配置
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx  # 用于 Embeddings

# 向量数据库（可选）
PINECONE_API_KEY=xxx
PINECONE_ENV=xxx

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **前端 `.env.local`**
```env
# ⚠️ 重要：Vite 项目必须使用 VITE_ 前缀

# 后端 API
VITE_API_BASE=http://127.0.0.1:8000/api

# WebSocket
VITE_WS_URL=ws://127.0.0.1:8000/ws

# Supabase（前端使用 anon key）
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_SUPABASE_BUCKET=media

# 功能开关
VITE_ENABLE_AI=true
VITE_ENABLE_FORUM=true
VITE_ENABLE_APU_HUB=true
```

---

## 🧪 测试账号

| 用户名 | 密码 | 学校 | 说明 |
|--------|------|------|------|
| alice | testpass123 | Peking University | 普通用户 |
| bob | testpass123 | Tsinghua University | 普通用户 |
| charlie | testpass123 | NUS | 普通用户 |
| admin | admin123 | APU | 管理员 |

**测试数据：**
- 5所大学、15个学院
- 10个用户、50条帖子
- 19个标签、150次点赞
- 100条评论、40个关注关系
- 5个交换项目、10个实习机会

---

## 🤖 Cursor AI 使用指南

### **项目上下文模板**
```markdown
【项目信息】
- 名称：学脉 UniPulse Asia
- 定位：亚太地区大学生社交+学术+职业平台
- 前端：Vite + React + TypeScript，环境变量用 VITE_
- 后端：Django + DRF，运行在 http://127.0.0.1:8000
- 实时：socket.io / Django Channels
- AI：Anthropic Claude + RAG
- 状态：Zustand
- 路由：react-router-dom
- Token：localStorage (xm_access_token / xm_refresh_token)

【技术约束】
1. 前端环境变量必须用 VITE_ 前缀
2. 代码中用 import.meta.env.VITE_*
3. 注册接口只接受 3 个字段（username/email/password）
4. 学校信息用两步注册（先创建账号，再更新 profile）
5. 所有幂等操作（点赞/收藏/关注）第二次调用=取消
6. 使用 react-router-dom，不是 Next.js
7. Token 存储 key：xm_access_token / xm_refresh_token

【当前任务】
[你的具体需求]
```

### **推荐模型**
| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 前端 UI 组件 | GPT-5 Codex-High | 代码优雅、UI 美观、Tailwind 最强 |
| 后端 API 开发 | claude-sonnet-4 | Django/DRF 经验最丰富 |
| AI/RAG 功能 | GPT-5 Thinking | 向量检索、复杂推理能力强 |
| Bug 修复 | claude-sonnet-4 | 边界情况处理最好 |
| 实时通信 | claude-sonnet-4 | WebSocket/Channels 经验丰富 |

### **有效提示词示例**

#### **添加新功能**
```markdown
你是 [Vite/Django] 工程师，请在学脉平台中添加 [功能名称]。

需求：
1. [具体需求]
2. [具体需求]

技术要求：
- 前端：使用 Zustand 管理状态
- 后端：遵循 DRF ViewSet 模式
- 实时：如需推送使用 socket.io
- 必须添加完整错误处理和类型定义

约束：
- 不要修改现有的认证/Feed/通知模块
- 环境变量必须用 VITE_ 前缀
- 遵循项目现有的目录结构

请生成完整代码并说明修改了哪些文件。
```

#### **Bug 修复**
```markdown
学脉平台遇到 [错误描述]。

错误信息：
```
[粘贴错误栈]
```

相关代码：
[粘贴代码]

项目上下文：
- Vite + React，环境变量用 VITE_
- Django + DRF 后端
- Token 存储在 localStorage

请分析原因并提供修复方案。
```

---

## ❓ 常见问题

### **Q1: 为什么注册返回 400 错误？**
**A:** 后端注册接口只接受 3 个字段（username/email/password）。不要传 `confirmPassword`、`university` 等字段。使用两步注册策略：
1. 先调用 `/api/auth/register/` 创建账号
2. 再调用 `/api/users/me/profile/update/` 更新学校信息

### **Q2: 环境变量不生效？**
**A:** 
1. Vite 项目必须用 `VITE_` 前缀
2. 代码中使用 `import.meta.env.VITE_*`
3. 修改 `.env.local` 后必须重启开发服务器（`Ctrl+C` → `npm run dev`）

### **Q3: CORS 错误？**
**A:** 检查后端 `config/settings/base.py`：
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

### **Q4: WebSocket 连接失败？**
**A:** 
1. 确认 Redis 正在运行
2. 检查 `VITE_WS_URL` 配置
3. 确认后端已安装 `python-socketio` 或 `channels`

### **Q5: AI 助手无响应？**
**A:** 
1. 检查 `ANTHROPIC_API_KEY` 是否正确
2. 确认有足够的 API 额度
3. 查看后端日志排查错误

### **Q6: 图片上传失败？**
**A:** 
1. 检查 Supabase Storage bucket 是否创建
2. 确认 bucket 策略允许上传
3. 检查文件大小限制（默认 50MB）

### **Q7: Celery 任务不执行？**
**A:** 
1. 确认 Redis 运行正常
2. 确认 Celery worker 已启动
3. 查看 Celery 日志：`celery -A config worker -l debug`

### **Q8: 如何重置数据库？**
**A:** 
```bash
# 开发环境重置（会删除所有数据）
find apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
python manage.py seed_full_data --clear
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [API 完整文档](docs/API_DOCUMENTATION.md) | 所有 API 端点详细说明 |
| [部署指南](docs/DEPLOYMENT_GUIDE.md) | Vercel + Railway 部署步骤 |
| [开发指南](docs/DEVELOPMENT_GUIDE.md) | 本地开发流程和规范 |
| [架构设计](docs/ARCHITECTURE.md) | 系统架构和数据流转 |
| [UI 规范](docs/UI_DESIGN.md) | 颜色、间距、组件风格 |

---

## 🚢 部署方案

### **前端：Vercel**
```bash
cd frontend
pnpm dev
vercel deploy --prod
```

### **后端：Railway**
```bash
# 环境变量配置在 Railway Dashboard
# 启动命令：gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### **数据库：Supabase**
- 新加坡区域
- PostgreSQL 15+
- 自动备份

### **存储：Supabase Storage / Cloudflare R2**
- Supabase：免费 1GB
- R2：免费 10GB

### **域名：Cloudflare**
- 前端：app.unipulse.asia → Vercel
- 后端：api.unipulse.asia → Railway

---

## 🎯 开发路线图

### **MVP（已完成 80%）✅**
- ✅ 用户认证（JWT）
- ✅ 社交 Feed（发帖/点赞/评论）
- ✅ 关注系统
- ✅ 通知系统
- ✅ 交换/实习信息
- 🔄 媒体上传

### **v1.1（开发中）🚧**
- 🔄 论坛系统（分区/话题/回复）
- 🔄 APU 信息中心
- 🔄 私信功能
- 🔄 WebSocket 实时推送

### **v1.2（计划中）📋**
- 📋 AI 助手（RAG）
- 📋 简历检查
- 📋 模拟面试
- 📋 内容审核

### **v2.0（未来）🔮**
- 🔮 拆分 AI 为独立服务
- 🔮 运营后台
- 🔮 数据看板
- 🔮 多语言支持
- 🔮 移动端 App

---

## 💰 成本预估

**MVP 阶段（月度）：**
| 服务 | 费用 | 说明 |
|------|------|------|
| Vercel | $0 | Hobby 计划 |
| Railway | $5-10 | 后端服务 |
| Supabase | $0 | 免费套餐 |
| Cloudflare R2 | $0-2 | 10GB 免费 |
| Claude API | $5-10 | 按使用付费 |
| **总计** | **$10-22/月** | |

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **项目主页：** [GitHub Repository]
- **问题反馈：** [GitHub Issues]
- **邮箱：** team@unipulse.asia
- **文档：** https://docs.unipulse.asia

---

<div align="center">
  <p><strong>学脉 UniPulse Asia</strong></p>
  <p>连接亚太，共享未来</p>
  <p>用 ❤️ 打造，服务大学生群体</p>
  <p>© 2025 UniPulse Asia. All rights reserved.</p>
  <p><strong>最后更新：</strong> 2025-10-31 | <strong>版本：</strong> v1.0-MVP</p>
</div>