from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SchoolViewSet, UniversityViewSet

router = DefaultRouter()
router.register(r"universities", UniversityViewSet, basename="university")
router.register(r"schools", SchoolViewSet, basename="school")

urlpatterns = [
    path("", include(router.urls)),
]
