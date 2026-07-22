from django.contrib import admin
from apps.student.models import Student, StudentDocument, Attendance


class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'full_name', 'phone', 'email',
        'gender', 'status', 'branch', 'enrolled_at', 'created_at',
    ]
    list_filter = ['status', 'gender', 'branch', 'source']
    search_fields = ['student_id', 'full_name', 'phone', 'email']


admin.site.register(Student, StudentAdmin)
admin.site.register(StudentDocument)
admin.site.register(Attendance)
