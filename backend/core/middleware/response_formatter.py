"""
统一响应格式中间件
"""
import json
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    """统一异常处理"""
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        # 格式化错误响应
        error_code = getattr(exc, 'default_code', 'error')
        
        # 处理不同类型的错误信息
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                error_message = exc.detail
            elif isinstance(exc.detail, list):
                error_message = '; '.join(str(e) for e in exc.detail)
            else:
                error_message = str(exc.detail)
        else:
            error_message = str(exc)
        
        custom_response = {
            "data": None,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        response.data = custom_response
    
    return response


class ResponseFormatterMiddleware:
    """格式化所有API响应"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 只处理API请求
        if request.path.startswith('/api/') and isinstance(response, JsonResponse):
            try:
                data = json.loads(response.content.decode('utf-8'))
                # 如果已经是标准格式，跳过
                if 'error' in data or 'data' in data:
                    return response
                
                # 格式化成功响应
                formatted_data = {
                    "data": data,
                    "paging": None,
                    "error": None
                }
                response.content = json.dumps(formatted_data).encode('utf-8')
            except:
                pass
        
        return response
