from rest_framework import serializers

from events.models import Label
from ..models import Event, EventStatus, EventMedia, EVENT_CREATE_CHOICES


class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ('media', )


class EventStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventStatus
        fields = ('status', )


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('name', )


class EventSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    labels = LabelSerializer(many=True)
    media = EventMediaSerializer(many=True)

    def get_status(self, obj):
        return str(obj.status.status)

    def get_user(self, obj):
        return str(obj.user)

    class Meta:
        model = Event
        fields = ('user', 'description', 'start', 'end', 'next_notification', 'period',
                  'periodic', 'status', 'labels', 'media')


class EventCreateSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=EVENT_CREATE_CHOICES)
    labels = serializers.ListField()
    media = serializers.FileField(required=False)

    def validate(self, attrs):
        status = attrs.get('status')
        attrs['status'] = EventStatus.objects.filter(status=status).first()
        return attrs

    def create(self, validated_data):
        label_list = validated_data.pop('labels')
        media = validated_data.pop('media')

        if label_list:
            existing_labels = Label.objects.filter(name__in=label_list)
            labels_to_create = set(label_list) - set(existing_labels.values_list('name', flat=True))

            all_labels = existing_labels
            if labels_to_create:
                Label.objects.bulk_create((Label(name=l) for l in labels_to_create))

                all_labels = Label.objects.filter(name__in=label_list)
            validated_data['labels'] = all_labels.values_list('id', flat=True)

        event = super(EventCreateSerializer, self).create(validated_data)

        if media:
            EventMedia.objects.create(media=media, event=event)
        return event

    class Meta:
        model = Event
        fields = ('description', 'start', 'end', 'next_notification', 'period', 'status', 'labels', 'media')
