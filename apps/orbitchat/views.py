from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.orbitchat.models import SyncState
from apps.orbitchat.serializers import SyncStateSerializer


@api_view(['GET', 'PATCH'])
@permission_classes([IsAdminUser])
def sync_state(request):
    state = SyncState.get()
    if request.method == 'PATCH':
        serializer = SyncStateSerializer(state, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(SyncStateSerializer(state).data)