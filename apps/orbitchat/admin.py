from django.contrib import admin

from apps.orbitchat.models import SyncState


@admin.register(SyncState)
class SyncStateAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_enabled', 'last_sync_at', 'updated_at')
    readonly_fields = ('key', 'last_sync_at', 'updated_at')