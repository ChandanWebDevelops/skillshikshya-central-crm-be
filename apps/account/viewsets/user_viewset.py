from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.account.models import User
from apps.account.serializers.user_serializer import UserSerializer
from apps.global_config.pagination import StandardResultsSetPagination
from apps.global_config.permissions import IsStaffOrSelf, IsStaffOrHasPermission


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)
