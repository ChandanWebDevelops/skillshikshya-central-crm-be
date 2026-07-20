from django.contrib import admin
from apps.course.models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_type', 'full_amount', 'one_time_payment_discount']
    list_filter = ['course_type']
    search_fields = ['name']


admin.site.register(Course, CourseAdmin)
