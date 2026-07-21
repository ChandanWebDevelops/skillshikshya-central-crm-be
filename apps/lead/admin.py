from django.contrib import admin

from apps.lead.models import (
    LeadSource, Campaign, LeadStatus, LeadPriority,
    LeadTag, LeadType, Lead, LeadCourseInterest, Enrollment, Payment,
    LeadCall, LeadActivity, FollowUp, LeadDocument,
)


class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'full_name', 'phone', 'email', 'lead_type', 'source',
        'status', 'priority', 'assigned_counselor', 'is_converted', 'is_archived', 'is_deleted', 'created_at',
    ]
    list_filter = ['lead_type', 'source', 'status', 'priority', 'is_converted', 'is_archived', 'is_deleted']
    search_fields = ['full_name', 'reference_number', 'phone', 'email']


admin.site.register(LeadSource)
admin.site.register(Campaign)
admin.site.register(LeadStatus)
admin.site.register(LeadPriority)
admin.site.register(LeadTag)
admin.site.register(LeadType)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadCourseInterest)
admin.site.register(Enrollment)
admin.site.register(Payment)
admin.site.register(LeadCall)
admin.site.register(LeadActivity)
admin.site.register(FollowUp)
admin.site.register(LeadDocument)
