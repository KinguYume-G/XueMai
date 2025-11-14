# Opportunities URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'exchange_programs', views.ExchangeProgramViewSet, basename='exchange-program')
router.register(r'internships', views.InternshipViewSet, basename='internship')
router.register(r'startups', views.StartupViewSet, basename='startup')

urlpatterns = [
    path('', include(router.urls)),
]
