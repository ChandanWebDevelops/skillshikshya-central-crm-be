from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from apps.account.serializers.group_serializer import GroupSerializer
from apps.global_config.pagination import CustomPagination


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
