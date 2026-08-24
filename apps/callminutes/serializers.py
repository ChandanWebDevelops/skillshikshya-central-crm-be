from rest_framework import serializers

from apps.callminutes.models import CallMinutesTransaction


class CallMinutesTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = CallMinutesTransaction
        fields = [
            'id', 'user', 'user_name', 'user_email', 'amount', 'type',
            'balance_after', 'call', 'note', 'created_by', 'created_by_name',
            'created_at',
        ]
        read_only_fields = fields