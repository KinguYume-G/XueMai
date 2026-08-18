"""Fast, isolated settings for the automated test suite."""

import os

os.environ.setdefault("SECRET_KEY", "xuemai-test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from .base import *  # noqa: E402,F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Build test tables directly from the current models. This keeps tests off the
# developer's Supabase database and avoids PostgreSQL-only migration SQL.
MIGRATION_MODULES = {
    "admin": None,
    "auth": None,
    "contenttypes": None,
    "sessions": None,
    "authentication": None,
    "campus": None,
    "users": None,
    "posts": None,
    "comments": None,
    "social": None,
    "notifications": None,
    "opportunities": None,
    "forums": None,
    "communities": None,
    "bookmarks": None,
    "ai": None,
    "uploads": None,
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
CELERY_TASK_ALWAYS_EAGER = True

