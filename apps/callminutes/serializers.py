from rest_framework import serializers

from apps.callminutes.models import CallMinutesTransaction


class CallMinutesTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    amount_minutes = serializers.SerializerMethodField()
    balance_after_minutes = serializers.SerializerMethodField()

    class Meta:
        model = CallMinutesTransaction
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'amount', 'amount_minutes', 'type',
            'balance_after', 'balance_after_minutes',
            'call', 'note', 'created_by', 'created_by_name',
            'created_at',
        ]
        read_only_fields = fields

    def get_amount_minutes(self, obj):
        return round(obj.amount / 60, 2)

    def get_balance_after_minutes(self, obj):
        return round(obj.balance_after / 60, 2)