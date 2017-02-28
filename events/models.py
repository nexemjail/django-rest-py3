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


class Event(models.Model):
    user = models.ForeignKey(User, related_name='events')
    description = models.TextField('Event description', null=True)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)
    periodic = models.BooleanField(default=False)
    period = models.DateTimeField(null=True)
    next_notification = models.DateTimeField(null=True)
    status = models.ForeignKey(EventStatus)


class EventMedia(models.Model):
    event = models.ForeignKey(Event, related_name='media')
    media = models.FileField(null=True)


class EventLabel(models.Model):
    event = models.ForeignKey(Event, related_name='labels')
    label = models.CharField(max_length=100)
