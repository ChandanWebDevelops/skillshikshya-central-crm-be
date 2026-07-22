from django.db import models
from django.conf import settings


class Course(models.Model):
    class CourseType(models.TextChoices):
        COURSE = 'course', 'Course'
        MASTER_CLASS = 'master_class', 'Master Class'
        JOB_READY_PROGRAM = 'job_ready_program', 'Job Ready Program'

    course_type = models.CharField(
        max_length=20, choices=CourseType.choices,
        verbose_name='Course Type',
    )
    name = models.CharField(max_length=255)
    full_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Full Amount',
    )
    one_time_payment_discount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name='One Time Payment Discount',
    )
    syllabus = models.URLField(max_length=500, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses_created',
    )

    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
