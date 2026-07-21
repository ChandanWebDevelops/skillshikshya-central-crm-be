import django_filters
from apps.branch.models import Branch


class BranchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Branch
        fields = ['name', 'code', 'is_active']
