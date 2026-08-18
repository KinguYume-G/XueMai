# Uploads URLs
from django.urls import path

from . import views

urlpatterns = [
    path("media/presign/", views.presign_upload, name="presign-upload"),
]
