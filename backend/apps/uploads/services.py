"""Supabase Storage helpers for browser-direct media uploads."""

from __future__ import annotations

import mimetypes
import os
import uuid
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from django.conf import settings
from django.utils import timezone


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES


def _validate_file(filename: str, mimetype: str, file_size: int | None = None) -> None:
    if mimetype not in ALLOWED_TYPES:
        raise ValueError(f"不支持的文件类型: {mimetype}")

    guessed_type, _ = mimetypes.guess_type(filename)
    if guessed_type and guessed_type != mimetype:
        jpeg_aliases = {guessed_type, mimetype} <= {"image/jpeg", "image/jpg"}
        if not jpeg_aliases:
            raise ValueError("文件扩展名与 MIME 类型不匹配")

    if file_size is not None:
        if file_size < 1:
            raise ValueError("文件不能为空")
        max_image_mb = int(getattr(settings, "MAX_IMAGE_MB", 10))
        max_video_mb = int(getattr(settings, "MAX_VIDEO_MB", 50))
        max_bytes = (max_image_mb if mimetype in ALLOWED_IMAGE_TYPES else max_video_mb) * 1024 * 1024
        if file_size > max_bytes:
            raise ValueError(f"文件超过 {max_bytes // 1024 // 1024}MB 限制")


def generate_presigned_upload_url(
    filename: str,
    mimetype: str,
    file_size: int | None = None,
) -> dict[str, object]:
    """Create a two-hour Supabase signed upload URL.

    The service-role key is used only server-side to mint the short-lived
    upload token.  It is never returned to the browser.
    """

    _validate_file(filename, mimetype, file_size)

    suffix = Path(filename).suffix.lower() or mimetypes.guess_extension(mimetype) or ".bin"
    now = timezone.now()
    file_path = f"uploads/{now.year}/{now.month:02d}/{uuid.uuid4().hex}{suffix}"

    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    bucket = (
        os.environ.get("SUPABASE_STORAGE_BUCKET")
        or os.environ.get("SUPABASE_BUCKET")
        or "media"
    )

    if not supabase_url or not service_key:
        raise RuntimeError("Supabase Storage 未配置")

    encoded_target = f"{quote(bucket, safe='')}/{quote(file_path, safe='/')}"
    endpoint = f"{supabase_url}/storage/v1/object/upload/sign/{encoded_target}"
    response = requests.post(
        endpoint,
        json={},
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )

    try:
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError("无法创建 Supabase 上传地址") from exc

    relative_url = payload.get("url") or payload.get("signedURL") or payload.get("signedUrl")
    if not relative_url:
        raise RuntimeError("Supabase 未返回上传地址")

    storage_base = f"{supabase_url}/storage/v1/"
    upload_url = (
        relative_url
        if str(relative_url).startswith(("http://", "https://"))
        else urljoin(storage_base, str(relative_url).lstrip("/"))
    )
    public_url = f"{supabase_url}/storage/v1/object/public/{encoded_target}"

    return {
        "uploadUrl": upload_url,
        "publicUrl": public_url,
        "path": file_path,
        "method": "PUT",
        "headers": {"Content-Type": mimetype, "x-upsert": "false"},
        "expiresIn": 7200,
    }
