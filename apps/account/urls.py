from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.account.viewsets.user_viewset import UserViewSet
from apps.account.viewsets.group_viewset import GroupViewSet
from apps.account.viewsets.permission_viewset import PermissionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
]
