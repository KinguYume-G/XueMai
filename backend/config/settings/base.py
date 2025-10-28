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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
