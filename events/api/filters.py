from django_filters import FilterSet
import django_filters

from ..models import Event


class EventListFilter(FilterSet):
    start = django_filters.IsoDateTimeFilter(name='start')
    starts_from = django_filters.IsoDateTimeFilter(name='start', lookup_expr='gte')
    starts_before = django_filters.IsoDateTimeFilter(name='start', lookup_expr='lte')

    end = django_filters.IsoDateTimeFilter(name='end')
    ends_before = django_filters.IsoDateTimeFilter(name='end', lookup_expr='lte')
    ends_after = django_filters.IsoDateTimeFilter(name='end', lookup_expr='gte')

    is_periodic = django_filters.BooleanFilter(name='periodic')

    period = django_filters.DurationFilter(name='period')
    period_less = django_filters.DurationFilter(name='period', lookup_expr='lte')
    period_more = django_filters.DurationFilter(name='period', lookup_expr='gte')

    next_notification = django_filters.IsoDateTimeFilter(name='next_notification')
    next_notification_before = django_filters.IsoDateTimeFilter(name='next_notification', lookup_expr='lte')
    next_notification_after = django_filters.IsoDateTimeFilter(name='next_notification', lookup_expr='gte')

    status = django_filters.CharFilter(name='status__status')

    description = django_filters.CharFilter(name='description', lookup_expr='icontains')

    class Meta:
        model = Event
