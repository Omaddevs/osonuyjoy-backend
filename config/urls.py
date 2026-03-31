from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from listings import auth_views
from listings import user_views
from listings.views import AdminReviewDetailView, AdminReviewListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/auth/register/", auth_views.RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", auth_views.LoginView.as_view(), name="auth-login"),
    path("api/auth/logout/", auth_views.LogoutView.as_view(), name="auth-logout"),
    path("api/auth/me/", auth_views.MeView.as_view(), name="auth-me"),
    path("api/user/profile/", user_views.UserProfileUpdateView.as_view(), name="user-profile"),
    path("api/user/favorites/", user_views.UserFavoritesListView.as_view(), name="user-favorites"),
    path("api/user/notifications/", user_views.UserNotificationsListView.as_view(), name="user-notifications"),
    path("api/user/notifications/read/", user_views.UserNotificationReadView.as_view(), name="user-notifications-read"),
    path(
        "api/admin/reviews/<int:pk>/",
        AdminReviewDetailView.as_view(),
        name="admin-review-detail",
    ),
    path(
        "api/admin/reviews/",
        AdminReviewListView.as_view(),
        name="admin-review-list",
    ),
    path("api/listings/", include("listings.urls")),
    path("api/reels/", include("reels.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
