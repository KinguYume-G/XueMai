# Comments URLs
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"comments", views.CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
