# Uploads views
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import generate_presigned_upload_url


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def presign_upload(request):
    """
    获取预签名上传URL
    
    请求:
        {
            "filename": "photo.jpg",
            "mimetype": "image/jpeg"
        }
    
    响应:
        {
            "data": {
                "uploadUrl": "...",
                "publicUrl": "...",
                "path": "..."
            },
            "error": null
        }
    """
    filename = request.data.get('filename')
    mimetype = request.data.get('mimetype')
    
    if not filename or not mimetype:
        return Response({
            'data': None,
            'error': {
                'code': 'missing_params',
                'message': '缺少filename或mimetype参数'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = generate_presigned_upload_url(filename, mimetype)
        return Response({
            'data': result,
            'error': None
        })
    except ValueError as e:
        return Response({
            'data': None,
            'error': {
                'code': 'invalid_file_type',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'data': None,
            'error': {
                'code': 'upload_error',
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

