# 本地开发与验收

本项目约定：前端运行在 `http://127.0.0.1:3000`，Django API 运行在
`http://127.0.0.1:8080`。Vite 会把同源的 `/api` 请求代理到 8080。

## 依赖

- Python 3.11 与 `backend/.venv311`
- Node.js 18+ 与 pnpm
- 已恢复并可连接的 Supabase Postgres；RAG 需要启用 `vector` 扩展并应用迁移
- Ollama；使用 Groq 时则需要有效的 `GROQ_API_KEY`

不要提交 `.env`、数据库口令、JWT 或 API key。复制
`backend/env.example` 为 `backend/.env`，填入自己的 Supabase 连接串和随机
`SECRET_KEY`。示例文件中的 `CHANGE_ME` 都必须替换。

如果只测试普通 CRUD，可以复制 `docker-compose.env.example` 为根目录
`.env`，再运行 `docker compose up -d db`。此基础镜像不包含 pgvector，因此
AI/RAG 联调仍应使用已经启用 pgvector 的 Supabase。

## 启动服务（PowerShell）

先启动 Ollama 并确认模型存在：

```powershell
ollama serve
ollama pull qwen3:8b
ollama pull nomic-embed-text
ollama list
```

新开终端启动后端：

```powershell
cd backend
$env:DJANGO_SETTINGS_MODULE = "config.settings.development"
.\.venv311\Scripts\python.exe manage.py migrate
.\.venv311\Scripts\python.exe -m uvicorn config.asgi:application --host 127.0.0.1 --port 8080
```

新开终端启动前端：

```powershell
cd frontend
pnpm.cmd install --frozen-lockfile
pnpm.cmd dev
```

打开 `http://127.0.0.1:3000`。API 文档位于
`http://127.0.0.1:8080/api/docs/`。若 3000 或 8080 被占用，先停止占用进程；
不要临时改成 8000，否则前后端约定会再次分叉。

## 自动检查

后端检查在隔离的内存 SQLite 中执行，不会写入 Supabase：

```powershell
cd backend
.\.venv311\Scripts\python.exe -m pytest -q
.\.venv311\Scripts\python.exe manage.py check --settings=config.settings.development
.\.venv311\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=config.settings.development
```

确认 Supabase 迁移状态（此命令会连接远程数据库）：

```powershell
cd backend
.\.venv311\Scripts\python.exe manage.py migrate --check --settings=config.settings.development
```

前端质量检查：

```powershell
cd frontend
pnpm.cmd exec tsc --noEmit
pnpm.cmd lint
pnpm.cmd build
```

上线前还应在真实生产环境变量下执行：

```powershell
cd backend
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
.\.venv311\Scripts\python.exe manage.py check --deploy
```

## 最小端到端验收

1. 注册新用户；用大小写不同的同一邮箱再次注册必须返回 400。
2. 使用邮箱和密码登录，刷新页面后仍保持登录；让 access token 失效后应能用 refresh token 自动续签。
3. 创建、查看、编辑和删除自己的内容，并验证其他用户不能修改。
4. 上传允许类型的小文件，并验证超限或不允许类型会返回清晰错误。
5. 在 AI 页面连续提问两轮，确认流式输出、会话上下文和历史记录正常。
6. 提交一条已入库知识能回答的问题，确认 RAG 命中 pgvector；关闭 Ollama 后应得到可识别的服务错误，而不是无限等待。
7. 检查浏览器 Network：业务请求必须发往 `/api/...` 并由 Vite 代理到 8080，不应出现 8000 或跨域错误。

只有自动检查全部通过、以上旅程在干净账号上通过、浏览器控制台无未处理错误，才算完成本地验收。
