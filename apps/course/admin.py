from django.contrib import admin
from apps.course.models import Course, Batch, CourseBatch


class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_type', 'full_amount', 'one_time_payment_discount']
    list_filter = ['course_type']
    search_fields = ['name']


class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


class CourseBatchAdmin(admin.ModelAdmin):
    list_display = ['coursebatch_id', 'name', 'course', 'batch', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'course', 'batch']
    search_fields = ['coursebatch_id', 'name']


admin.site.register(Course, CourseAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(CourseBatch, CourseBatchAdmin)