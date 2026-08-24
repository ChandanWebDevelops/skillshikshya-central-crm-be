from django.contrib import admin

from apps.invoices.models import Invoice, InvoiceEmailConfig


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'type', 'course_name', 'amount',
        'total_paid_so_far', 'remaining_balance', 'emailed_to', 'sent_at',
    )
    list_filter = ('type',)
    search_fields = ('invoice_number', 'course_name', 'emailed_to')
    readonly_fields = [f.name for f in Invoice._meta.fields]


admin.site.register(InvoiceEmailConfig)