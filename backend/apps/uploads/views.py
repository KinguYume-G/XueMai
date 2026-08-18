# Uploads views
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import generate_presigned_upload_url


@api_view(["POST"])
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
    filename = request.data.get("filename")
    mimetype = request.data.get("mimetype")
    raw_file_size = request.data.get("file_size")

    if not filename or not mimetype:
        return Response(
            {
                "data": None,
                "error": {"code": "missing_params", "message": "缺少filename或mimetype参数"},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        file_size = int(raw_file_size) if raw_file_size is not None else None
        result = generate_presigned_upload_url(filename, mimetype, file_size)
        return Response({"data": result, "error": None})
    except (TypeError, ValueError) as e:
        return Response(
            {"data": None, "error": {"code": "invalid_file_type", "message": str(e)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError:
        return Response(
            {
                "data": None,
                "error": {
                    "code": "storage_unavailable",
                    "message": "暂时无法创建上传地址，请稍后重试",
                },
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
