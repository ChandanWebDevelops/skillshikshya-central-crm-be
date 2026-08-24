import django_filters

from apps.callminutes.models import CallMinutesTransaction


class CallMinutesTransactionFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = CallMinutesTransaction
        fields = ['type']