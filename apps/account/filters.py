import django_filters
from django.contrib.auth.models import Group
from apps.account.models import User


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    designation = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.ModelChoiceFilter(
        field_name='groups', queryset=Group.objects.all(),
    )
    branch_id = django_filters.NumberFilter(field_name='branch')
    branch__in = django_filters.BaseInFilter(field_name='branch', lookup_expr='in')
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = [
            'name', 'email', 'designation', 'phone',
            'group', 'branch', 'is_active', 'is_staff',
        ]
