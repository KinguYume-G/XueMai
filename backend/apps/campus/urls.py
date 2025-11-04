from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, SchoolViewSet

router = DefaultRouter()
router.register(r"universities", UniversityViewSet, basename="university")
router.register(r"schools", SchoolViewSet, basename="school")

urlpatterns = [
    path("", include(router.urls)),
]

