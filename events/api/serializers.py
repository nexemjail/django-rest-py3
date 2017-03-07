from datetime import timedelta
from django.db.models import Max, Min, F

from rest_framework import serializers

from events.models import Label, EVENT_CHOICES, EVENT_STATUSES
from ..models import Event, EventStatus, EventMedia, EVENT_CREATE_CHOICES


def validate_period(attrs, instance=None):

    period = attrs.get('period')
    periodic = attrs.get('periodic')

    if instance:
        period = period or instance.period
        periodic = periodic or instance.periodic

    if (period and periodic) or (not period and not periodic):
        return attrs

    raise serializers.ValidationError(dict(period='Period and periodic flag must match!'
                                                  ' (Periodic -> period is not null)'))


class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ('media', )


class EventStatusSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return EventStatus.objects.create(validated_data['status'])

    class Meta:
        model = EventStatus
        fields = ('status', )


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('name', )


class EventSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=EVENT_CHOICES, source='status.status')
    labels = LabelSerializer(many=True, required=False)
    media = EventMediaSerializer(many=True, required=False)

    def validate_status(self, status):
        if EventStatus.objects.filter(status=status).first():
            return status
        raise serializers.ValidationError('Invalid "status"')

    def get_user(self, obj):
        return str(obj.user)

    def validate(self, attrs):
        return validate_period(attrs, self.instance)

    def update(self, instance, validated_data):
        # TODO: handle media
        media = validated_data.pop('media', None)

        labels = validated_data.pop('labels', [])
        instance.labels = Label.create_all(list(map(lambda x: x['name'], labels))) if labels else []

        instance.description = validated_data.get('description', instance.description)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('start', instance.end)
        instance.next_notification = validated_data.get('next_notification', instance.next_notification)

        status = validated_data.get('status')
        instance.status = EventStatus.objects.filter(status=status.get('status')).first() if status else instance.status

        instance.periodic = validated_data.get('periodic', instance.periodic)
        instance.period = validated_data.get('period', instance.period)
        instance.place = validated_data.get('place', instance.place)
        instance.save()

        return instance

    class Meta:
        model = Event
        fields = ('id', 'user', 'description', 'start', 'end', 'next_notification', 'period',
                  'periodic', 'status', 'place', 'labels', 'media')


class EventCreateSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=EVENT_CREATE_CHOICES)
    labels = serializers.ListField()
    period = serializers.DurationField(default=None, required=False, allow_null=True)
    media = serializers.FileField(required=False)

    def validate_status(self, attr):
        return EventStatus.objects.filter(status=attr).first()

    def validate(self, attrs):
        if attrs.get('period') and not attrs.get('periodic'):
            raise serializers.ValidationError({'period': 'Periodic flag must be set if period is defined'})

        next_notification = attrs.get('next_notification')
        attrs['next_notification'] = next_notification if next_notification else attrs['start'] - timedelta(minutes=5)

        if attrs['end']:
            # TODO: pass user here!
            start, end = attrs['start'], attrs['end']

            # Enhance this to be as fast as dick!
            # overlapping_events_count = Event.objects.filter(end__isnull=False)\
            #     .annotate(max=Max(start, 'start')).annotate(min=Min('end', end)).filter(max__lte=F('min')).count()

            user = self.context.get('request').user
            events = Event.objects.filter(end__isnull=False, user=user)
            for e in events:
                if max(e.start, start) <= min(e.end, end):
                    raise serializers.ValidationError('Event is overlapping with others!')

        return validate_period(attrs)

    def create(self, validated_data):
        label_list = validated_data.pop('labels', None)
        media = validated_data.pop('media', None)

        validated_data['labels'] = Label.create_all(label_list)

        if 'next_notification' not in validated_data:
            validated_data['next_notification'] = validated_data['start'] - timedelta(minutes=5)

        event = super(EventCreateSerializer, self).create(validated_data)

        if media:
            EventMedia.objects.create(media=media, event=event)
        return event

    class Meta:
        model = Event
        fields = ('id', 'description', 'start', 'end', 'next_notification', 'period',
                  'periodic', 'status', 'labels', 'media')
