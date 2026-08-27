from rest_framework import serializers

from apps.account.models import User
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


class UserCallBalanceSerializer(serializers.ModelSerializer):
    remaining_minutes = serializers.SerializerMethodField()
    balance_display = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()
    recent_topups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email',
            'call_seconds_balance', 'remaining_minutes', 'balance_display',
            'recent_transactions', 'recent_topups',
        ]

    def get_remaining_minutes(self, obj):
        return obj.call_seconds_balance // 60

    def get_balance_display(self, obj):
        balance = obj.call_seconds_balance
        return f'{balance // 60}:{str(balance % 60).zfill(2)}'

    def _recent(self, obj, attr):
        return CallMinutesTransactionSerializer(
            getattr(obj, attr, []), many=True,
        ).data

    def get_recent_transactions(self, obj):
        return self._recent(obj, '_recent_transactions')

    def get_recent_topups(self, obj):
        return self._recent(obj, '_recent_topups')