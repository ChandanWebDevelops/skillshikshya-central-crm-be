from django.contrib import admin

from apps.lead.models import (
    LeadSource, Campaign, LeadStatus, LeadPriority,
    LeadTag, Lead, LeadCall, LeadActivity, FollowUp, LeadDocument,
)


class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'phone', 'email', 'lead_type', 'source',
        'status', 'priority', 'assigned_counselor', 'is_converted', 'created_at',
    ]
    list_filter = ['lead_type', 'source', 'status', 'priority', 'is_converted']
    search_fields = ['full_name', 'phone', 'email']


admin.site.register(LeadSource)
admin.site.register(Campaign)
admin.site.register(LeadStatus)
admin.site.register(LeadPriority)
admin.site.register(LeadTag)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadCall)
admin.site.register(LeadActivity)
admin.site.register(FollowUp)
admin.site.register(LeadDocument)
