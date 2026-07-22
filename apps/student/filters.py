import django_filters
from apps.student.models import Student, StudentDocument, Attendance


class StudentFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    notes = django_filters.CharFilter(lookup_expr='icontains')
    guardian_name = django_filters.CharFilter(lookup_expr='icontains')
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    enrolled_at__gte = django_filters.DateFilter(field_name='enrolled_at', lookup_expr='gte')
    enrolled_at__lte = django_filters.DateFilter(field_name='enrolled_at', lookup_expr='lte')

    class Meta:
        model = Student
        fields = {
            'gender': ['exact'],
            'status': ['exact', 'in'],
            'source': ['exact', 'in'],
            'branch': ['exact', 'in'],
            'assigned_counselor': ['exact'],
        }


class StudentDocumentFilter(django_filters.FilterSet):
    class Meta:
        model = StudentDocument
        fields = ['student', 'document_type']


class AttendanceFilter(django_filters.FilterSet):
    date__gte = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date__lte = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Attendance
        fields = {
            'student': ['exact'],
            'course': ['exact'],
            'status': ['exact'],
        }
