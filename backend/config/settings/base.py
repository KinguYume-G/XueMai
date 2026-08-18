# config/settings/base.py  —— 顶部 import + DATABASES（可直接整段替换）

import os
from pathlib import Path

import dj_database_url
import environ

# 1) 项目根目录（按你的结构，base.py 在 config/settings/ 下，往上 2 层到 backend/）
BASE_DIR = Path(__file__).resolve().parents[2]

# urls & entrypoints（必须显式设置）
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# 2) 读取 backend/.env（没有就跳过）
env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# SECRET_KEY
SECRET_KEY = env("SECRET_KEY")

# DEBUG (默认从环境变量读取，开发环境会在 development.py 中覆盖)
DEBUG = env.bool("DEBUG", default=False)

# ALLOWED_HOSTS
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# AI Configuration
GROQ_API_KEY = env("GROQ_API_KEY", default="")
GROQ_MODEL = env("GROQ_MODEL", default="qwen/qwen3.6-27b")


# 3) 拿 DATABASE_URL；如果不存在或是空字符串，回退到 SQLite
db_url = env(
    "DATABASE_URL",
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
)

# 4) 用 dj-database-url 解析 Supabase 连接串，并开启连接复用 / 健康检查
DATABASES = {
    "default": dj_database_url.parse(
        db_url,
        conn_max_age=60,  # 连接复用 60 秒，减少频繁建连
        conn_health_checks=True,  # 健康检查，自动清理坏连接
    )
}

# 5) 追加超时参数（可选但推荐）
#    注意：端口 6543 已经在 .env 的 DATABASE_URL 里设置好了，
#    这里不用再写 PORT。
DATABASES["default"].setdefault("OPTIONS", {})
DATABASES["default"]["OPTIONS"].setdefault("connect_timeout", 10)
# 如果想要 SQL 执行超时 30 秒，可以取消下一行注释：
# DATABASES["default"]["OPTIONS"].setdefault("options", "-c statement_timeout=30000")


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 基础必需配置，确保 admin 能加载
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # Local apps
    "apps.authentication",
    "apps.campus",
    "apps.users",
    "apps.posts",
    "apps.comments",
    "apps.social",
    "apps.notifications",
    "apps.opportunities",
    "apps.forums",
    "apps.communities",
    "apps.bookmarks",
    "apps.ai",
    "apps.uploads",
    "apps.search",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
MAX_IMAGE_MB = env.int("MAX_IMAGE_MB", default=10)
MAX_VIDEO_MB = env.int("MAX_VIDEO_MB", default=50)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# ========== REST Framework Configuration ==========
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.middleware.response_formatter.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "core.throttling.AnonymousRateThrottle",
        "core.throttling.AuthenticatedRateThrottle",
    ],
}

# ========== JWT Configuration ==========
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
}

# ========== CORS Configuration ==========
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
)
CORS_ALLOW_CREDENTIALS = True

# ========== drf-spectacular Configuration ==========
SPECTACULAR_SETTINGS = {
    "TITLE": "学脉 | UniPulse Asia API",
    "DESCRIPTION": "Academic social network connecting students across Asia-Pacific universities",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ============================================
# RAG 向量检索配置
# ============================================

# 向量检索后端选择
# 'pgvector': 使用 PostgreSQL pgvector 扩展（推荐）
RAG_VECTOR_BACKEND = env.str("RAG_VECTOR_BACKEND", default="pgvector")
EMBEDDING_MODEL = env.str("EMBEDDING_MODEL", default="nomic-embed-text")
VECTOR_DIMENSION = env.int("VECTOR_DIMENSION", default=768)

# pgvector 检索参数
RAG_PGVECTOR_TOP_K = env.int("RAG_PGVECTOR_TOP_K", default=5)  # 默认返回结果数
RAG_PGVECTOR_SIMILARITY_THRESHOLD = env.float(
    "RAG_PGVECTOR_SIMILARITY_THRESHOLD", default=0.3
)  # 相似度阈值（0-1）

# 开发环境建议使用 pgvector 进行测试
# 生产环境切换时，在 .env 文件中设置：
# RAG_VECTOR_BACKEND=pgvector

# ============================================
# AI 客户端配置
# ============================================

# AI 客户端类型选择
# 'ollama': 本地 Ollama 服务（免费，需要本地运行）
# 'groq': Groq 云端 API（快速，需要 API key）
# 'deepseek': DeepSeek 云端 API（备用）
AI_CLIENT_TYPE = env.str("AI_CLIENT_TYPE", default="groq")

# Ollama 配置
OLLAMA_BASE_URL = env.str("OLLAMA_BASE_URL", default="http://localhost:11434")
OLLAMA_MODEL = env.str("OLLAMA_MODEL", default="qwen3:8b")
OLLAMA_TIMEOUT = env.int("OLLAMA_TIMEOUT", default=60)
OLLAMA_THINK = env.bool("OLLAMA_THINK", default=False)

# Groq 配置
GROQ_API_KEY = env.str("GROQ_API_KEY", default="")
GROQ_MODEL = env.str("GROQ_MODEL", default="qwen/qwen3.6-27b")
GROQ_BASE_URL = env.str("GROQ_BASE_URL", default="https://api.groq.com/openai/v1")
GROQ_TIMEOUT = env.int("GROQ_TIMEOUT", default=30)

# DeepSeek 配置（备用）
DEEPSEEK_API_KEY = env.str("DEEPSEEK_API_KEY", default="")
DEEPSEEK_MODEL = env.str("DEEPSEEK_MODEL", default="deepseek-chat")
DEEPSEEK_BASE_URL = env.str("DEEPSEEK_BASE_URL", default="https://api.deepseek.com")
DEEPSEEK_TIMEOUT = env.int("DEEPSEEK_TIMEOUT", default=60)
