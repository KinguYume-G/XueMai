# Social URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'follows', views.FollowViewSet, basename='follow')

urlpatterns = [
    path('follow/', views.follow_user, name='follow-user'),
    path('', include(router.urls)),
]
