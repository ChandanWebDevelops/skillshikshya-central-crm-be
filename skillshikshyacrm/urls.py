from django.contrib import admin
from django.urls import path, include
from apps.account.auth_views import (
    RegisterView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenBlacklistView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', CookieTokenObtainPairView.as_view(), name='auth_login'),
    path('api/auth/refresh/', CookieTokenRefreshView.as_view(), name='auth_refresh'),
    path('api/auth/logout/', CookieTokenBlacklistView.as_view(), name='auth_logout'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),
    path('api/', include('apps.account.urls')),
    path('api/', include('apps.course.urls')),

]
