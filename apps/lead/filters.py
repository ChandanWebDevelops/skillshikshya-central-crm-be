import django_filters
from apps.lead.models import (
    LeadSource, Campaign, LeadStatus, LeadPriority,
    LeadTag, Lead, LeadCall, LeadActivity, FollowUp, LeadDocument,
)


class LeadSourceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LeadSource
        fields = ['name', 'is_active']


class CampaignFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Campaign
        fields = ['name', 'source', 'is_active']


class LeadStatusFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LeadStatus
        fields = ['name', 'is_active', 'is_final']


class LeadPriorityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LeadPriority
        fields = ['name', 'is_active']


class LeadTagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LeadTag
        fields = ['name', 'is_active']


class LeadFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    notes = django_filters.CharFilter(lookup_expr='icontains')
    lead_score__gte = django_filters.NumberFilter(field_name='lead_score', lookup_expr='gte')
    lead_score__lte = django_filters.NumberFilter(field_name='lead_score', lookup_expr='lte')
    expected_revenue__gte = django_filters.NumberFilter(field_name='expected_revenue', lookup_expr='gte')
    expected_revenue__lte = django_filters.NumberFilter(field_name='expected_revenue', lookup_expr='lte')
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    next_followup_at__gte = django_filters.DateTimeFilter(field_name='next_followup_at', lookup_expr='gte')
    next_followup_at__lte = django_filters.DateTimeFilter(field_name='next_followup_at', lookup_expr='lte')

    class Meta:
        model = Lead
        fields = {
            'lead_type': ['exact'],
            'source': ['exact', 'in'],
            'campaign': ['exact', 'in'],
            'branch': ['exact', 'in'],
            'priority': ['exact'],
            'status': ['exact', 'in'],
            'assigned_counselor': ['exact'],
            'primary_course': ['exact'],
            'is_converted': ['exact'],
            'tags': ['exact'],
        }


class LeadCallFilter(django_filters.FilterSet):
    caller = django_filters.CharFilter(lookup_expr='icontains')
    notes = django_filters.CharFilter(lookup_expr='icontains')
    call_timestamp__gte = django_filters.DateTimeFilter(field_name='call_timestamp', lookup_expr='gte')
    call_timestamp__lte = django_filters.DateTimeFilter(field_name='call_timestamp', lookup_expr='lte')

    class Meta:
        model = LeadCall
        fields = ['lead', 'direction', 'outcome']


class LeadActivityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LeadActivity
        fields = ['lead', 'activity_type', 'performed_by']


class FollowUpFilter(django_filters.FilterSet):
    scheduled_at__gte = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='gte')
    scheduled_at__lte = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='lte')

    class Meta:
        model = FollowUp
        fields = ['lead', 'assigned_to', 'status']


class LeadDocumentFilter(django_filters.FilterSet):
    class Meta:
        model = LeadDocument
        fields = ['lead', 'document_type']
