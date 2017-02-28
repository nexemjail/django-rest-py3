from rest_framework import serializers, validators
from ..models import Event, EventStatus, EventLabel, EventMedia, EVENT_CREATE_CHOICES


class EventMediaSerializer(serializers.ModelSerializer):

    media_url = serializers.URLField()

    class Meta:
        model = EventMedia
        fields = ('event_id', )


class EventStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventStatus
        fields = ('status', )


class EventSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    status = EventStatusSerializer()

    def get_user(self, obj):
        return str(obj)

    class Meta:
        model = Event
        fields = ('user', 'description', 'start', 'end', 'next_notification', 'period', 'status')


class EventCreateSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=EVENT_CREATE_CHOICES)

    def validate(self, attrs):
        status = attrs.get('status')
        attrs['status'] = EventStatus.objects.filter(status=status).first()
        return attrs

    class Meta:
        model = Event
        fields = ('description', 'start', 'end', 'next_notification', 'period', 'status')