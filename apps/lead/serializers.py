from rest_framework import serializers
from apps.lead.models import (
    LeadSource, Campaign, LeadStatus, LeadPriority,
    LeadTag, Lead, LeadCall, LeadActivity, FollowUp, LeadDocument,
)


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatus
        fields = '__all__'


class LeadPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadPriority
        fields = '__all__'


class LeadTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadTag
        fields = '__all__'


class LeadMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'phone', 'status', 'priority', 'lead_type', 'lead_score']


class LeadListSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    priority_name = serializers.CharField(source='priority.name', read_only=True)
    priority_color = serializers.CharField(source='priority.color', read_only=True)
    status_color = serializers.CharField(source='status.color', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    assigned_counselor_name = serializers.CharField(source='assigned_counselor.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    primary_course_name = serializers.CharField(source='primary_course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)

    class Meta:
        model = Lead
        fields = '__all__'


class LeadSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    priority_name = serializers.CharField(source='priority.name', read_only=True)
    priority_color = serializers.CharField(source='priority.color', read_only=True)
    status_color = serializers.CharField(source='status.color', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    assigned_counselor_name = serializers.CharField(source='assigned_counselor.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    primary_course_name = serializers.CharField(source='primary_course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)

    call_count = serializers.SerializerMethodField()
    next_followup = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_converted', 'converted_at',
        ]

    def get_call_count(self, obj):
        return obj.calls.count()

    def get_next_followup(self, obj):
        followup = obj.followups.filter(status='pending').order_by('scheduled_at').first()
        if followup:
            return {
                'id': followup.id,
                'scheduled_at': followup.scheduled_at,
                'purpose': followup.purpose,
                'assigned_to': followup.assigned_to_id,
                'assigned_to_name': followup.assigned_to.name if followup.assigned_to else None,
            }
        return None


class LeadCallSerializer(serializers.ModelSerializer):
    caller_name = serializers.CharField(source='caller', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = LeadCall
        fields = '__all__'
        read_only_fields = ['lead', 'created_by', 'created_at']


class LeadActivitySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.name', read_only=True)

    class Meta:
        model = LeadActivity
        fields = '__all__'
        read_only_fields = ['lead', 'created_at']


class FollowUpSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)

    class Meta:
        model = FollowUp
        fields = '__all__'
        read_only_fields = ['lead', 'created_by', 'updated_by', 'created_at', 'updated_at']


class LeadDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)

    class Meta:
        model = LeadDocument
        fields = '__all__'
        read_only_fields = ['lead', 'uploaded_by', 'uploaded_at']
