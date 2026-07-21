import csv
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from apps.lead.models import (
    LeadSource, Campaign, LeadStatus, LeadPriority,
    LeadTag, Lead, LeadCourseInterest, Enrollment, Payment,
    LeadCall, LeadActivity, FollowUp, LeadDocument,
)
from apps.lead.serializers import (
    LeadSourceSerializer, CampaignSerializer, LeadStatusSerializer,
    LeadPrioritySerializer, LeadTagSerializer, LeadSerializer,
    LeadCourseInterestSerializer, EnrollmentSerializer, PaymentSerializer,
    LeadCallSerializer, LeadActivitySerializer, FollowUpSerializer,
    LeadDocumentSerializer, LeadListSerializer, LeadMinSerializer,
)
from apps.lead.filters import (
    LeadSourceFilter, CampaignFilter, LeadStatusFilter,
    LeadPriorityFilter, LeadTagFilter, LeadFilter,
    LeadCourseInterestFilter, EnrollmentFilter, PaymentFilter,
    LeadCallFilter, LeadActivityFilter, FollowUpFilter, LeadDocumentFilter,
)
from apps.global_config.pagination import CustomPagination
from apps.global_config.permissions import IsStaffOrHasPermission


class ConfigViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class LeadSourceViewSet(ConfigViewSet):
    queryset = LeadSource.objects.all()
    serializer_class = LeadSourceSerializer
    filterset_class = LeadSourceFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'is_active']
    ordering = ['name']


class CampaignViewSet(ConfigViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    filterset_class = CampaignFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'start_date', 'end_date']
    ordering = ['name']


class LeadStatusViewSet(ConfigViewSet):
    queryset = LeadStatus.objects.all()
    serializer_class = LeadStatusSerializer
    filterset_class = LeadStatusFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'sort_order', 'is_final']
    ordering = ['sort_order', 'name']


class LeadPriorityViewSet(ConfigViewSet):
    queryset = LeadPriority.objects.all()
    serializer_class = LeadPrioritySerializer
    filterset_class = LeadPriorityFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'sort_order']
    ordering = ['sort_order', 'name']


class LeadTagViewSet(ConfigViewSet):
    queryset = LeadTag.objects.all()
    serializer_class = LeadTagSerializer
    filterset_class = LeadTagFilter
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'is_active']
    ordering = ['name']


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related(
        'source', 'campaign', 'branch', 'priority', 'status',
        'assigned_counselor', 'primary_course', 'created_by', 'updated_by',
    ).prefetch_related('tags')
    pagination_class = CustomPagination
    filterset_class = LeadFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'phone', 'email', 'notes', 'reference_number']
    ordering_fields = [
        'id', 'reference_number', 'full_name', 'lead_score', 'expected_revenue',
        'created_at', 'updated_at', 'last_contact_at', 'next_followup_at',
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return LeadSerializer
        if self.action == 'export_csv':
            return LeadMinSerializer
        return LeadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'recycle_bin':
            return qs.filter(is_deleted=True)
        if self.action == 'export_csv':
            return qs.filter(is_deleted=False).select_related('source', 'status', 'priority', 'assigned_counselor')
        qs = qs.filter(is_deleted=False)
        include_archived = self.request.query_params.get('include_archived', '').lower() in ('true', '1')
        if not include_archived:
            qs = qs.filter(is_archived=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'purge']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Full Name', 'Phone', 'Email', 'Lead Type',
            'Source', 'Status', 'Priority', 'Assigned Counselor',
            'Lead Score', 'Expected Revenue', 'Is Converted',
            'Created At', 'Updated At',
        ])
        for lead in queryset.iterator(chunk_size=500):
            writer.writerow([
                lead.reference_number, lead.full_name, lead.phone, lead.email,
                lead.lead_type,
                lead.source.name if lead.source else '',
                lead.status.name if lead.status else '',
                lead.priority.name if lead.priority else '',
                lead.assigned_counselor.name if lead.assigned_counselor else '',
                lead.lead_score, lead.expected_revenue,
                lead.is_converted,
                lead.created_at, lead.updated_at,
            ])
        return response

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        lead = self.get_object()
        lead.is_archived = True
        lead.save(update_fields=['is_archived'])
        return Response({'detail': 'Lead archived.'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        lead = self.get_object()
        lead.is_archived = False
        lead.save(update_fields=['is_archived'])
        return Response({'detail': 'Lead restored.'})

    @action(detail=True, methods=['post'])
    def purge(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can permanently delete leads.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        lead = Lead._base_manager.filter(pk=pk).first()
        if not lead:
            return Response({'detail': 'Lead not found.'}, status=status.HTTP_404_NOT_FOUND)
        lead.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def recycle_bin(self, request):
        self.action = 'recycle_bin'
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LeadListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LeadListSerializer(queryset, many=True)
        return Response(serializer.data)


class LeadCourseInterestViewSet(viewsets.ModelViewSet):
    serializer_class = LeadCourseInterestSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LeadCourseInterestFilter
    ordering_fields = ['created_at']
    ordering = ['-is_primary', '-created_at']

    def get_queryset(self):
        return LeadCourseInterest.objects.filter(lead_id=self.kwargs['lead_pk']).select_related('course')

    def perform_create(self, serializer):
        serializer.save(lead_id=self.kwargs['lead_pk'])

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EnrollmentFilter
    ordering_fields = ['enrollment_date', 'created_at']
    ordering = ['-enrollment_date']

    def get_queryset(self):
        return Enrollment.objects.filter(lead_id=self.kwargs['lead_pk']).select_related(
            'course', 'student', 'created_by', 'updated_by',
        ).prefetch_related('payments')

    def perform_create(self, serializer):
        serializer.save(
            lead_id=self.kwargs['lead_pk'],
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'created_at']
    ordering = ['-payment_date']

    def get_queryset(self):
        return Payment.objects.filter(
            enrollment_id=self.kwargs['enrollment_pk'],
            enrollment__lead_id=self.kwargs['lead_pk'],
        ).select_related('received_by')

    def perform_create(self, serializer):
        serializer.save(
            enrollment_id=self.kwargs['enrollment_pk'],
            received_by=self.request.user,
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class LeadCallViewSet(viewsets.ModelViewSet):
    serializer_class = LeadCallSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LeadCallFilter
    ordering_fields = ['call_timestamp', 'duration_seconds']
    ordering = ['-call_timestamp']

    def get_queryset(self):
        return LeadCall.objects.filter(lead_id=self.kwargs['lead_pk']).select_related('created_by')

    def perform_create(self, serializer):
        serializer.save(
            lead_id=self.kwargs['lead_pk'],
            created_by=self.request.user,
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class LeadActivityViewSet(viewsets.ModelViewSet):
    serializer_class = LeadActivitySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LeadActivityFilter
    ordering_fields = ['activity_at']
    ordering = ['-activity_at']

    def get_queryset(self):
        return LeadActivity.objects.filter(lead_id=self.kwargs['lead_pk']).select_related('performed_by')

    def perform_create(self, serializer):
        serializer.save(
            lead_id=self.kwargs['lead_pk'],
            performed_by=self.request.user,
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FollowUpFilter
    ordering_fields = ['scheduled_at']
    ordering = ['-scheduled_at']

    def get_queryset(self):
        return FollowUp.objects.filter(lead_id=self.kwargs['lead_pk']).select_related(
            'assigned_to', 'created_by', 'updated_by',
        )

    def perform_create(self, serializer):
        serializer.save(
            lead_id=self.kwargs['lead_pk'],
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


class LeadDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = LeadDocumentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LeadDocumentFilter
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        return LeadDocument.objects.filter(lead_id=self.kwargs['lead_pk']).select_related('uploaded_by')

    def perform_create(self, serializer):
        serializer.save(
            lead_id=self.kwargs['lead_pk'],
            uploaded_by=self.request.user,
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsStaffOrHasPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]
