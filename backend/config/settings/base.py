# config/settings/base.py  —— 顶部 import + DATABASES（可直接整段替换）

from pathlib import Path
import os
import environ
import dj_database_url


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
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-change-in-production-123456789")

# DEBUG (默认从环境变量读取，开发环境会在 development.py 中覆盖)
DEBUG = env.bool("DEBUG", default=False)

# ALLOWED_HOSTS
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# 3) 拿 DATABASE_URL；如果不存在或是空字符串，回退到 SQLite
db_url = env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")

# 4) 用 dj-database-url 解析，并开启连接复用
DATABASES = {
    "default": dj_database_url.parse(
        db_url,
        conn_max_age=120,
        conn_health_checks=True,
    )
}

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
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# ========== drf-spectacular Configuration ==========
SPECTACULAR_SETTINGS = {
    "TITLE": "学脉 | UniPulse Asia API",
    "DESCRIPTION": "Academic social network connecting students across Asia-Pacific universities",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
