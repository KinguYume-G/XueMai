# Forums URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'faculties', views.FacultyViewSet, basename='faculty')
router.register(r'forums', views.ForumViewSet, basename='forum')
router.register(r'topics', views.TopicViewSet, basename='topic')

urlpatterns = [
    path('forums/overview/', views.forum_overview, name='forum-overview'),
    path('topics/hot/', views.hot_topics, name='topics-hot'),
    path('', include(router.urls)),
]

