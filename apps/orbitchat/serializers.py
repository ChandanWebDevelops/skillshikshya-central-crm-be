from rest_framework import serializers

from apps.orbitchat.models import SyncState


class SyncStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncState
        fields = ['key', 'is_enabled', 'last_sync_at', 'updated_at']
        read_only_fields = ['key', 'last_sync_at', 'updated_at']