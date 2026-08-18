# Generated migration to enable pgvector extension
# 必须在 0004 之前运行，因为 0004 使用了 vector 类型

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0003_aiconversation_aimessage_and_more'),
    ]

    # 这个迁移会被重新编号为 0004，原来的 0004 会变成 0005
    run_before = [
        ('ai', '0004_alter_aiembedding_embedding_vector'),
    ]

    operations = [
        # 启用 pgvector 扩展（用于向量存储）
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS vector;',
            reverse_sql='DROP EXTENSION IF EXISTS vector;',
        ),
    ]
