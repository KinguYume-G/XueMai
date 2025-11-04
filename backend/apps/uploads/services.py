"""
Supabase存储服务
"""
import os
import uuid
from datetime import datetime, timedelta
from django.conf import settings


def generate_presigned_upload_url(filename, mimetype):
    """
    生成Supabase预签名上传URL
    
    参数:
        filename: 原始文件名
        mimetype: MIME类型
    
    返回:
        {
            'uploadUrl': str,  # 预签名上传URL
            'publicUrl': str,  # 公开访问URL
            'path': str        # 存储路径
        }
    """
    # 验证mimetype
    allowed_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    allowed_video_types = ['video/mp4', 'video/webm', 'video/quicktime']
    allowed_types = allowed_image_types + allowed_video_types
    
    if mimetype not in allowed_types:
        raise ValueError(f"不支持的文件类型: {mimetype}")
    
    # 生成唯一文件路径: uploads/2025/10/uuid.ext
    now = datetime.now()
    ext = os.path.splitext(filename)[1] or '.jpg'
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = f"uploads/{now.year}/{now.month:02d}/{unique_filename}"
    
    # 获取Supabase配置
    supabase_url = os.environ.get('SUPABASE_URL', '')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    bucket_name = os.environ.get('SUPABASE_BUCKET', 'uploads')
    
    if not supabase_url or not supabase_key:
        # 开发环境：返回本地上传路径
        return {
            'uploadUrl': f'/api/media/upload/',  # 本地上传端点
            'publicUrl': f'/media/{file_path}',
            'path': file_path,
            'method': 'POST'
        }
    
    try:
        from supabase import create_client
        
        # 创建Supabase客户端
        supabase = create_client(supabase_url, supabase_key)
        
        # 生成签名URL (有效期1小时)
        signed_url = supabase.storage.from_(bucket_name).create_signed_url(
            file_path,
            expires_in=3600
        )
        
        # 公开URL
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
        
        return {
            'uploadUrl': signed_url,
            'publicUrl': public_url,
            'path': file_path
        }
    
    except Exception as e:
        # 如果Supabase不可用，回退到本地
        return {
            'uploadUrl': f'/api/media/upload/',
            'publicUrl': f'/media/{file_path}',
            'path': file_path,
            'method': 'POST',
            'error': str(e)
        }

