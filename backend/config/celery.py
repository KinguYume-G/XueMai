import os
from celery import Celery

# 指定 Django 配置模块（根据你项目实际来改）
# 如果你的 DJANGO_SETTINGS_MODULE 在 .env 里是：config.settings.development
# 那这里就写成 'config.settings.development'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各 app 下的 tasks.py
app.autodiscover_tasks()
