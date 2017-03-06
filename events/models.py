from django.contrib.auth.models import User
from django.db import models

EVENT_STATUSES = ('W', 'P', 'C')
EVENT_CHOICES = (
    ('W', 'Waiting'),
    ('C', 'Cancelled'),
    ('P', 'Passed'),
)
EVENT_CREATE_CHOICES = (
    ('W', 'Waiting'),
    ('P', 'Passed'),
)


class EventStatus(models.Model):
    status = models.CharField(max_length=1, choices=EVENT_CHOICES)


class Label(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def create_non_existing(cls, labels_list):
        existing_labels = Label.objects.filter(name__in=labels_list).values_list('name', flat=True)
        not_existing_labels = set(labels_list) - set(existing_labels)

        Label.objects.bulk_create((Label(name=name) for name in not_existing_labels))

    @classmethod
    def create_all(cls, label_list):
        Label.create_non_existing(label_list)
        return Label.objects.filter(name__in=label_list)


class Event(models.Model):
    user = models.ForeignKey(User, related_name='events')
    description = models.TextField('Event description', null=True)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)
    periodic = models.BooleanField(default=False)
    period = models.DurationField(null=True)
    next_notification = models.DateTimeField(null=True)
    place = models.CharField(max_length=500, null=True)
    status = models.ForeignKey(EventStatus)
    labels = models.ManyToManyField(Label, 'events')


class EventMedia(models.Model):
    event = models.ForeignKey(Event, related_name='media')
    media = models.FileField(null=True)



