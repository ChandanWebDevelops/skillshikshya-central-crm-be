from django.contrib import admin

from apps.callminutes.models import CallMinutesTransaction


@admin.register(CallMinutesTransaction)
class CallMinutesTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'balance_after', 'created_at')
    list_filter = ('type',)
    search_fields = ('user__email', 'note')
    readonly_fields = [f.name for f in CallMinutesTransaction._meta.fields]