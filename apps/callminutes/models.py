from django.conf import settings
from django.db import models


class CallMinutesTransaction(models.Model):
    class Type(models.TextChoices):
        TOPUP = 'topup', 'Top Up'
        DEDUCTION = 'deduction', 'Deduction'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='call_minutes_transactions',
    )
    amount = models.IntegerField(help_text='Positive for top-up, negative for deduction.')
    type = models.CharField(max_length=12, choices=Type.choices)
    balance_after = models.IntegerField()
    call = models.ForeignKey(
        'lead.LeadCall', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='minute_transactions',
    )
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'call_minutes_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.amount:+d} -> {self.balance_after} ({self.type})'