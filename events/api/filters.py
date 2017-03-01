from django_filters import FilterSet
import django_filters

from ..models import Event


class EventListFilter(FilterSet):
    start = django_filters.DateFilter(name='start')
    starts_from = django_filters.DateFilter(name='start', lookup_expr='gte')
    starts_before = django_filters.DateFilter(name='start', lookup_expr='lte')

    end = django_filters.DateFilter(name='end')
    ends_before = django_filters.DateFilter(name='end', lookup_expr='lte')
    ends_after = django_filters.DateFilter(name='end', lookup_expr='gte')

    is_periodic = django_filters.BooleanFilter(name='periodic')

    period = django_filters.DateTimeFilter(name='period')
    period_less_than = django_filters.DateTimeFilter(name='period', lookup_expr='lte')
    period_greater_than = django_filters.DateTimeFilter(name='period', lookup_expr='gte')

    next_notification = django_filters.DateTimeFilter(name='next_notification')
    next_notification_less_than = django_filters.DateTimeFilter(name='next_notification', lookup_expr='lte')
    next_notification_greater_than = django_filters.DateTimeFilter(name='next_notification', lookup_expr='gte')

    status = django_filters.CharFilter(name='status__status')

    description = django_filters.CharFilter(name='description', lookup_expr='icontains')

    class Meta:
        model = Event
