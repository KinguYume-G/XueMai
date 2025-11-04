from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.AIDocumentViewSet, basename='ai-document')
router.register(r'chunks', views.AIChunkViewSet, basename='ai-chunk')
router.register(r'query_logs', views.AIQueryLogViewSet, basename='ai-query-log')

urlpatterns = [
    path('query/', views.ai_query, name='ai-query'),
    path('', include(router.urls)),
]

