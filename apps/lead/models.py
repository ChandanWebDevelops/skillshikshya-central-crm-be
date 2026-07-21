from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Sum


class LeadSource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'lead_sources'
        ordering = ['name']

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    source = models.ForeignKey(
        LeadSource, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='campaigns',
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['name']

    def __str__(self):
        return self.name


class LeadStatus(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#2563eb')
    sort_order = models.IntegerField(default=0)
    is_final = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'lead_statuses'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class LeadPriority(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#6b7280')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'lead_priorities'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class LeadTag(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#2563eb')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'lead_tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class LeadType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'lead_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Lead(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    lead_type = models.ForeignKey(
        LeadType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    custom_data = models.JSONField(default=dict)
    source = models.ForeignKey(
        LeadSource, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    priority = models.ForeignKey(
        LeadPriority, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    status = models.ForeignKey(
        LeadStatus, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    assigned_counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_leads',
    )
    lead_score = models.IntegerField(default=0)
    primary_course = models.ForeignKey(
        'course.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads',
    )
    expected_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    next_followup_at = models.DateTimeField(null=True, blank=True)
    last_contact_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(LeadTag, blank=True, related_name='leads')
    is_converted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads_deleted',
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference_number} - {self.full_name} ({self.phone})'

    def save(self, *args, **kwargs):
        if not self.reference_number:
            year = datetime.now().year
            prefix = f'LD-{year}'
            last = Lead.objects.filter(reference_number__startswith=prefix).order_by('reference_number').last()
            seq = 1
            if last:
                seq = int(last.reference_number.split('-')[-1]) + 1
            self.reference_number = f'{prefix}-{seq:06d}'
        super().save(*args, **kwargs)


class LeadCourseInterest(models.Model):
    class InterestLevel(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='course_interests')
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='lead_interests')
    is_primary = models.BooleanField(default=False)
    interest_level = models.CharField(
        max_length=10, choices=InterestLevel.choices, default=InterestLevel.MEDIUM,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_course_interests'
        ordering = ['-is_primary', '-created_at']
        unique_together = ['lead', 'course']

    def __str__(self):
        return f'{self.lead.full_name} → {self.course.name}'


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        DROPPED_OUT = 'dropped_out', 'Dropped Out'
        TRANSFERRED = 'transferred', 'Transferred'

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(
        'student.Student', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrollments',
    )
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='enrollments')
    batch = models.CharField(max_length=255, null=True, blank=True)
    enrollment_date = models.DateField()
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING,
    )
    listed_fee = models.DecimalField(max_digits=12, decimal_places=2)
    standard_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    additional_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrollments_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrollments_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        ordering = ['-enrollment_date']

    def __str__(self):
        return f'{self.lead.reference_number} → {self.course.name} ({self.status})'

    @property
    def total_paid(self):
        result = self.payments.filter(status='successful').aggregate(Sum('amount'))
        return result['amount__sum'] or 0

    @property
    def remaining_amount(self):
        return self.agreed_amount - self.total_paid

    @property
    def is_full_paid(self):
        return self.remaining_amount <= 0


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        ESEWA = 'esewa', 'eSewa'
        KHALTI = 'khalti', 'Khalti'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CARD = 'card', 'Card'
        CONNECT_IPS = 'connectips', 'ConnectIPS'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESSFUL = 'successful', 'Successful'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        VOIDED = 'voided', 'Voided'

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name='payments',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH,
    )
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING,
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payments_received',
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.amount} ({self.get_status_display()}) — {self.enrollment}'


class LeadCall(models.Model):
    class Direction(models.TextChoices):
        INBOUND = 'inbound', 'Inbound'
        OUTBOUND = 'outbound', 'Outbound'

    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name='calls',
    )
    call_timestamp = models.DateTimeField()
    direction = models.CharField(
        max_length=10, choices=Direction.choices, default=Direction.OUTBOUND,
    )
    caller = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    duration_seconds = models.IntegerField(default=0)
    outcome = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    recording_url = models.URLField(max_length=500, null=True, blank=True)
    next_followup_at = models.DateTimeField(null=True, blank=True)
    next_action = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='lead_calls_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_calls'
        ordering = ['-call_timestamp']

    def __str__(self):
        return f'{self.get_direction_display()} - {self.caller} ({self.call_timestamp})'


class LeadActivity(models.Model):
    class ActivityType(models.TextChoices):
        CALL = 'call', 'Call'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        NOTE = 'note', 'Note'
        MEETING = 'meeting', 'Meeting'
        STATUS_CHANGE = 'status_change', 'Status Change'
        ASSIGNMENT_CHANGE = 'assignment_change', 'Assignment Change'
        DEMO_CLASS = 'demo_class', 'Demo Class'
        PAYMENT = 'payment', 'Payment'
        ENROLLMENT = 'enrollment', 'Enrollment'

    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name='activities',
    )
    activity_type = models.CharField(
        max_length=20, choices=ActivityType.choices,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='activities_performed',
    )
    activity_at = models.DateTimeField()
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_activities'
        ordering = ['-activity_at']

    def __str__(self):
        return f'{self.get_activity_type_display()} - {self.title}'


class FollowUp(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        MISSED = 'missed', 'Missed'
        CANCELLED = 'cancelled', 'Cancelled'

    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name='followups',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='followups_assigned',
    )
    scheduled_at = models.DateTimeField()
    purpose = models.TextField(null=True, blank=True)
    reminder_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='followups_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='followups_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead_followups'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'FollowUp for {self.lead.full_name} at {self.scheduled_at}'


class LeadDocument(models.Model):
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name='documents',
    )
    document_type = models.CharField(max_length=255)
    file = models.URLField(max_length=500)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents_uploaded',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lead_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.document_type} - {self.lead.full_name}'
