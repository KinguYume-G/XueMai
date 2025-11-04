# Root URL configuration
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # JWT Authentication (legacy)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # App APIs
    path("api/", include("apps.authentication.urls")),
    path("api/", include("apps.campus.urls")),
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.posts.urls")),
    path("api/", include("apps.comments.urls")),
    path("api/", include("apps.social.urls")),
    path("api/", include("apps.notifications.urls")),
    path("api/", include("apps.opportunities.urls")),
    path("api/", include("apps.forums.urls")),
    path("api/", include("apps.uploads.urls")),
    path("api/ai/", include("apps.ai.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
