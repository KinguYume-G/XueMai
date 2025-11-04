# ASGI configuration for WebSocket support
# asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")  # 或 base.py 对应路径
application = get_asgi_application()  # 先跑通，再接入 socket/channels
