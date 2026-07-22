from django.conf import settings
from django.db import models


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        GRADUATED = 'graduated', 'Graduated'
        DROPPED = 'dropped', 'Dropped'
        TRANSFERRED = 'transferred', 'Transferred'

    student_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_phone = models.CharField(max_length=20, null=True, blank=True)
    guardian_relation = models.CharField(max_length=100, null=True, blank=True)

    emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)

    source = models.ForeignKey(
        'lead.LeadSource', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students',
    )
    lead = models.ForeignKey(
        'lead.Lead', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students',
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students',
    )
    assigned_counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students_assigned',
    )
    enrolled_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    photo_url = models.URLField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student_id} - {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.student_id:
            year = self.enrolled_at.year if self.enrolled_at else 2026
            prefix = f'STU-{year}'
            last = Student.objects.filter(student_id__startswith=prefix).order_by('student_id').last()
            seq = 1
            if last:
                seq = int(last.student_id.split('-')[-1]) + 1
            self.student_id = f'{prefix}-{seq:04d}'
        super().save(*args, **kwargs)


class StudentDocument(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='documents',
    )
    document_type = models.CharField(max_length=255)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='student_documents',
    )
    file = models.URLField(max_length=500)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='student_docs_uploaded',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.document_type} - {self.student.full_name}'
