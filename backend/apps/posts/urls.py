# Posts URLs
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"posts", views.PostViewSet, basename="post")
router.register(r"tags", views.TagViewSet, basename="tag")

urlpatterns = [
    path("feed/", views.PostViewSet.as_view({"get": "feed"}), name="feed"),
    path("", include(router.urls)),
]
