# 学脉 UniPulse Asia — System Architecture

This document describes the current architecture of the codebase, as verified against
`backend/config/settings/`, `backend/requirements.txt`, `backend/apps/`, and
`frontend/package.json`. It replaces the architecture sections of the old root-level
`UniPulse_Asia_终极完整版技术方案.md` planning document, most of which described a future/aspirational
tech stack (LangChain/LangGraph, Vercel/Railway hosting, etc.) that is not what the
current code implements.

## Product summary

- **Name:** 学脉 UniPulse Asia
- **Positioning:** AI-native cross-border education & social platform for Asia-Pacific
  university students.
- **Core surfaces:** social feed (posts/comments/likes/bookmarks), forums, communities,
  exchange programs, internships/opportunities, an AI assistant toolbox, notifications,
  and search.

## Repository layout

This is a monorepo:

- `backend/` — Django 5.2 + Django REST Framework API.
- `frontend/` — React 18 + TypeScript + Vite single-page app.
- `docker-compose.yml` — local PostgreSQL container only (production/Supabase deployments
  do not use this compose file; see comment at the top of that file).

## Backend

### Stack (verified from `backend/requirements.txt`)

- Django 5.2.7, Django REST Framework 3.15.2, `djangorestframework_simplejwt` 5.5.1 for JWT auth
- PostgreSQL via `psycopg` 3.2.10, with `pgvector` 0.4.1 for vector search
  (Supabase-hosted in production; local Postgres via `docker-compose.yml` for development)
- Redis 6.x (`redis` package) + Celery 5.5.3 + `channels_redis` for background jobs / caching
- `django-cors-headers`, `django-filter`, `django-storages`, `whitenoise`
- `drf-spectacular` for OpenAPI schema generation (`api/schema/`, `api/docs/` routes in
  `backend/config/urls.py`)
- ChromaDB/LangChain-Chroma packages are commented out in `requirements.txt` — the project
  migrated off ChromaDB to pgvector (see `docs/data-pipeline.md`).

### Django apps (`backend/apps/`, all registered in `INSTALLED_APPS`)

| App | Responsibility |
|---|---|
| `authentication` | JWT auth endpoints, registration/login |
| `campus` | University/school/faculty reference data |
| `users` | User accounts and profiles |
| `posts` | Social feed posts |
| `comments` | Comments on posts |
| `social` | Follows/likes and other social graph actions |
| `notifications` | Notification feed |
| `opportunities` | Internships, exchange programs, startups |
| `forums` | Forums and topics |
| `communities` | Communities (interest/city/campus/study-group) |
| `bookmarks` | Bookmarking posts/opportunities |
| `ai` | AI assistant toolbox, orchestrator, RAG (see below) |
| `uploads` | File upload handling |
| `search` | Global search across users/posts/topics/communities/opportunities |

### AI subsystem (`backend/apps/ai/`)

- **Client factory** (`apps/ai/clients/`): `get_ai_client()` builds one of three
  interchangeable LLM clients — `GroqClient`, `DeepSeekClient`, `OllamaClient` — selected via
  `settings.AI_CLIENT_TYPE` (defaults to Groq). This is a 3-provider setup, not the
  Groq+Ollama-only "dual engine" described in the old planning doc.
- **Workflow orchestrator** (`apps/ai/orchestrator/`): `WorkflowOrchestrator` executes a
  configured set of steps as a dependency-ordered DAG (topological execution with optional
  steps and per-step error handling), yielding progress events for streaming responses.
  Steps live in `apps/ai/orchestrator/steps/` and include `rag_retrieve_step`,
  `llm_generate_step`, `file_process_step`, and `validation_step`. `views_orchestrator.py`
  and `apps/ai/views.py` expose this over HTTP/SSE.
- **Function catalog** (`apps/ai/config/functions.yaml`): 21 AI function definitions
  (career, academic, entrepreneurship, writing/tools categories), each pointing at a system
  prompt file under `apps/ai/prompts/` and optionally enabling RAG context.
- **RAG** (`apps/ai/services/rag_engine.py`, `vector_search_service.py`): retrieval against
  a PostgreSQL/pgvector-backed knowledge base populated by the data pipeline described in
  `docs/data-pipeline.md`.

### Config

- `backend/config/settings/base.py` / `production.py` — environment-driven settings, no
  hardcoded hosting provider (Railway/Vercel references in the old planning doc do not
  appear anywhere in the actual settings files).
- `backend/config/urls.py` — root URL conf, mounts each app's `urls.py` under `api/`.

## Frontend

### Stack (verified from `frontend/package.json`)

- React 18.3 + TypeScript, built with Vite 5
- `react-router-dom` 6 for routing (`frontend/src/routes/index.tsx`)
- `zustand` for client-side state (used by list/detail pages like Exchange/Internships)
- `axios`-based API client (`frontend/src/lib/api/client.ts`) with a typed service layer
  under `frontend/src/services/api/*`
- Tailwind CSS + `class-variance-authority` + `tailwind-merge` for styling, with a small
  local shadcn-style UI kit under `frontend/src/components/ui/`
- `i18next` / `react-i18next` for localization
- `react-markdown` + `react-syntax-highlighter` for rendering AI chat responses

### Routing

`frontend/src/routes/index.tsx` defines a single router tree wrapped in `Protected` (auth
gate) + `AppLayout` (shared chrome). Pages are organized as flat files under
`frontend/src/pages/` for most features, with per-feature folders (`Exchange/`,
`Internships/`) where a list + detail pair exists.

## Deployment

- Local development: `docker-compose.yml` runs a local Postgres 16 container; the Django
  dev server and Vite dev server run outside Docker.
- Production: environment-variable-driven (`config/settings/production.py`), using a
  Supabase-hosted Postgres instance (per the comment in `docker-compose.yml`).
