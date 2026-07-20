from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.account.models import User
from apps.account.serializers.user_serializer import UserSerializer
from apps.global_config.pagination import CustomPagination
from apps.global_config.permissions import IsStaffOrSelf, IsStaffOrHasPermission


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_perm('account.view_user'):
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]
