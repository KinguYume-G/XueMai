from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class AuthenticationAPITests(TestCase):
    password = "StrongPass123!"

    def setUp(self):
        self.client = APIClient()

    def register(self, **overrides):
        payload = {
            "username": "new-user",
            "email": "New.User@Example.com",
            "password": self.password,
            "password_confirm": self.password,
        }
        payload.update(overrides)
        return self.client.post("/api/auth/register/", payload, format="json")

    def test_register_normalizes_email_and_returns_token_pair(self):
        response = self.register(email="  New.User@Example.com  ")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["error"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])

        user = User.objects.get(username="new-user")
        self.assertEqual(user.email, "new.user@example.com")
        self.assertTrue(hasattr(user, "profile"))

    def test_register_rejects_case_insensitive_duplicate_email(self):
        User.objects.create_user(
            username="existing-user",
            email="existing@example.com",
            password=self.password,
        )

        response = self.register(email="Existing@Example.COM")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data["error"]["message"]
        self.assertIn("email", errors)
        self.assertIn("该邮箱已被注册。", str(errors["email"]))

    def test_database_constraint_rejects_case_insensitive_duplicate(self):
        User.objects.create_user(
            username="first-user",
            email="unique@example.com",
            password=self.password,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="second-user",
                    email="UNIQUE@EXAMPLE.COM",
                    password=self.password,
                )

    def test_login_accepts_trimmed_case_insensitive_email(self):
        User.objects.create_user(
            username="login-user",
            email="login@example.com",
            password=self.password,
        )

        response = self.client.post(
            "/api/auth/login/",
            {"email": "  LOGIN@Example.COM ", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user"]["username"], "login-user")
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])

    def test_login_fails_closed_for_historical_duplicate_rows(self):
        with patch.object(
            User.objects,
            "get",
            side_effect=User.MultipleObjectsReturned,
        ):
            response = self.client.post(
                "/api/auth/login/",
                {"email": "duplicate@example.com", "password": self.password},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"]["code"], "invalid_credentials")

    def test_refresh_issues_a_new_access_token(self):
        register_response = self.register()
        refresh = register_response.data["data"]["refresh"]

        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
