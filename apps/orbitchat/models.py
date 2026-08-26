from django.db import models


class SyncState(models.Model):
    """Singleton-per-key watermark for external sync jobs."""

    key = models.CharField(max_length=50, unique=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    is_enabled = models.BooleanField(
        default=False,
        help_text='When false, scheduled (automatic) runs are skipped.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orbitchat_sync_states'

    def __str__(self):
        return f'{self.key}: enabled={self.is_enabled} last={self.last_sync_at}'

    @classmethod
    def get(cls, key='orbitchat_leads'):
        obj, _ = cls.objects.get_or_create(key=key)
        return obj