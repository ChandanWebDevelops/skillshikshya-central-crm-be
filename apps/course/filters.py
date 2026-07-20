import django_filters
from apps.course.models import Course


class CourseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    course_type = django_filters.ChoiceFilter(choices=Course.CourseType.choices)

    class Meta:
        model = Course
        fields = ['name', 'course_type']
