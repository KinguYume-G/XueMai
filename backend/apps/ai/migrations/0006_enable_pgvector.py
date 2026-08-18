# Generated migration to enable pgvector extension
# 必须在所有使用 vector 类型的迁移之前运行

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0003_aiconversation_aimessage_and_more'),
    ]

    operations = [
        # 启用 pgvector 扩展（用于向量存储）
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS vector;',
            reverse_sql='DROP EXTENSION IF EXISTS vector;',
        ),
    ]
