"""
rebuild_embeddings.py

用于重建所有 AIChunk 向量的脚本。

通过 manage.py shell 执行:
python manage.py shell < scripts/rebuild_embeddings.py
"""

import os
import sys
from time import sleep
from django.conf import settings

# --- Django 环境设置 ---
# 确保脚本可以独立运行，也能在Django shell中运行
# 当通过 `manage.py shell` 运行时，Django环境已自动加载

# 将项目根目录添加到Python路径，以便导入应用模块
# 'backend/scripts' -> 'backend'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- 向量生成逻辑 ---

# 导入Django模型和所需的库
print("--- 开始导入模块 ---")
try:
    from apps.ai.models import AIChunk, AIEmbedding
    from langchain_ollama import OllamaEmbeddings
    from tqdm import tqdm
    print("模块导入成功。")
except ImportError as e:
    print(f"错误：导入模块失败 - {e}")
    print("请确保 Django 环境配置正确，且已安装 langchain_ollama, tqdm。")
    # 如果在非shell环境中运行，这里会退出
    if 'manage' not in sys.argv[0]:
        sys.exit(1)


# 定义向量模型配置（与 RAGEngine 保持一致）
# Ollama 服务地址，可以从环境变量读取，提供默认值
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
# 使用和RAG引擎相同的模型
EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL


def get_embedding_client():
    """
    初始化并返回一个 embedding client 实例。
    """
    try:
        print(f"正在连接 Ollama 服务: {OLLAMA_BASE_URL}...")
        client = OllamaEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
        )
        # 尝试连接，确保服务可用
        client.embed_query("test")
        print("Ollama 连接成功。")
        return client
    except Exception as e:
        print(f"错误：无法初始化 Ollama embedding client - {e}")
        print("请确保 Ollama 服务正在运行，并且可以通过上面的地址访问。")
        return None

def run():
    """
    主执行函数
    """
    print("\n--- 开始重建向量任务 ---")

    embedding_client = get_embedding_client()
    if not embedding_client:
        print("任务终止。")
        return

    # 1. 获取所有 AIChunk
    chunks = AIChunk.objects.all().order_by('id')
    total_chunks = chunks.count()

    if total_chunks == 0:
        print("数据库中没有找到 AIChunk，任务结束。")
        return

    print(f"准备处理 {total_chunks} 个文本块 (AIChunks)。")

    # 2. 初始化计数器
    success_count = 0
    failure_count = 0
    
    # 使用 tqdm 创建进度条
    chunk_iterator = chunks.iterator() # 使用 iterator 减少内存占用
    progress_bar = tqdm(chunk_iterator, total=total_chunks, desc="重建向量中")

    # 3. 遍历并处理每个 chunk
    for chunk in progress_bar:
        try:
            # 获取或创建对应的 AIEmbedding 记录
            embedding_obj, created = AIEmbedding.objects.get_or_create(chunk=chunk)
            
            if created:
                progress_bar.set_postfix_str(f"Chunk {chunk.id}: 创建了新的Embedding记录")
            else:
                progress_bar.set_postfix_str(f"Chunk {chunk.id}: 更新已有的Embedding记录")

            # 生成向量
            chunk_content = chunk.content.strip()
            if not chunk_content:
                # 如果内容为空，标记为失败并跳过
                failure_count += 1
                tqdm.write(f"警告: Chunk {chunk.id} 内容为空，已跳过。")
                continue

            vector = embedding_client.embed_query(chunk_content)

            # 更新 AIEmbedding 记录
            embedding_obj.embedding_vector = vector
            embedding_obj.embedding_model = EMBEDDING_MODEL_NAME
            embedding_obj.save()

            success_count += 1
            
            # 短暂休眠，避免请求过于频繁 (可选)
            # sleep(0.01)

        except Exception as e:
            failure_count += 1
            # 使用 tqdm.write 避免破坏进度条显示
            tqdm.write(f"错误: 处理 Chunk {chunk.id} 失败 - {e}")
            continue

    # 4. 打印最终结果
    print("\n--- 任务完成 ---")
    print(f"总共处理文本块: {total_chunks}")
    print(f"  - 成功: {success_count}")
    print(f"  - 失败/跳过: {failure_count}")
    print("--------------------")

# --- 脚本入口 ---
# 只有在直接执行或通过shell导入时才运行
if __name__ == "__main__" or 'shell' in sys.argv:
    run()
