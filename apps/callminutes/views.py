from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.account.models import User
from apps.callminutes.models import CallMinutesTransaction
from apps.callminutes.serializers import CallMinutesTransactionSerializer
from apps.callminutes.services import add_minutes
from apps.global_config.pagination import CustomPagination


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_call_minutes(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    amount = request.data.get('amount')
    note = request.data.get('note', '')
    target, txn = add_minutes(
        user_id=target.id,
        amount=amount,
        note=note,
        created_by=request.user,
    )
    return Response({
        'detail': f'Added {txn.amount} call minutes to {target.email}.',
        'user': {'id': target.id, 'email': target.email},
        'balance': target.call_minutes_balance,
        'transaction': CallMinutesTransactionSerializer(txn).data,
    }, status=status.HTTP_200_OK)


class CallMinutesTransactionListView(generics.ListAPIView):
    serializer_class = CallMinutesTransactionSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return (
            CallMinutesTransaction.objects
            .filter(user_id=self.kwargs['user_id'])
            .select_related('user', 'created_by', 'call')
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_call_minutes(request):
    recent = CallMinutesTransaction.objects.filter(user=request.user)[:10]
    return Response({
        'balance': request.user.call_minutes_balance,
        'recent_transactions': CallMinutesTransactionSerializer(recent, many=True).data,
    })