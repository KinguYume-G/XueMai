"""
认证路由
"""
from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/me/', views.get_current_user, name='current-user'),
    path('auth/me/profile/', views.update_profile, name='update-profile'),
]
