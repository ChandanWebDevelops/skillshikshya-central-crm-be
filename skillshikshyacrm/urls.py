from django.contrib import admin
from django.urls import path, include
from apps.account.auth_views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenBlacklistView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', CookieTokenObtainPairView.as_view(), name='auth_login'),
    path('api/auth/refresh/', CookieTokenRefreshView.as_view(), name='auth_refresh'),
    path('api/auth/logout/', CookieTokenBlacklistView.as_view(), name='auth_logout'),
    path('api/', include('apps.account.urls')),
]
