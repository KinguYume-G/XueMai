from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.uploads.services import generate_presigned_upload_url


class SignedUploadServiceTests(TestCase):
    @override_settings(MAX_IMAGE_MB=1, MAX_VIDEO_MB=2)
    @patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://project.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "service-secret",
            "SUPABASE_STORAGE_BUCKET": "media",
        },
        clear=False,
    )
    @patch("apps.uploads.services.requests.post")
    def test_creates_signed_upload_url_without_leaking_service_key(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "url": "/object/upload/sign/media/uploads/2026/01/file.jpg?token=signed-token"
        }
        post.return_value = response

        result = generate_presigned_upload_url("photo.jpg", "image/jpeg", 512)

        self.assertEqual(result["method"], "PUT")
        self.assertIn("token=signed-token", result["uploadUrl"])
        self.assertIn("/object/public/media/", result["publicUrl"])
        self.assertNotIn("service-secret", str(result))
        self.assertEqual(post.call_args.kwargs["timeout"], 10)

    def test_rejects_mime_extension_mismatch(self):
        with self.assertRaisesMessage(ValueError, "不匹配"):
            generate_presigned_upload_url("payload.exe", "image/png", 100)

    @override_settings(MAX_IMAGE_MB=1)
    def test_rejects_oversized_image(self):
        with self.assertRaisesMessage(ValueError, "1MB"):
            generate_presigned_upload_url("photo.png", "image/png", 2 * 1024 * 1024)


class SignedUploadApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="uploader", email="uploader@example.com", password="safe-pass-123"
        )

    def test_requires_authentication(self):
        response = self.client.post(
            "/api/media/presign/",
            {"filename": "photo.jpg", "mimetype": "image/jpeg", "file_size": 100},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    @patch("apps.uploads.views.generate_presigned_upload_url")
    def test_returns_unwrapped_signed_upload_contract(self, generate):
        generate.return_value = {"uploadUrl": "https://signed", "publicUrl": "https://public"}
        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/api/media/presign/",
            {"filename": "photo.jpg", "mimetype": "image/jpeg", "file_size": 100},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["uploadUrl"], "https://signed")
        generate.assert_called_once_with("photo.jpg", "image/jpeg", 100)
