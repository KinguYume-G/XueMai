import os
from celery import Celery

# 指定 Django 配置模块（根据你项目实际来改）
# 如果你的 DJANGO_SETTINGS_MODULE 在 .env 里是：config.settings.development
# 那这里就写成 'config.settings.development'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')

# 从环境变量里读取 Redis / Celery 配置
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL')),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL')),
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# 自动发现各 app 下的 tasks.py
app.autodiscover_tasks()
