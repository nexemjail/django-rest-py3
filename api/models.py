from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    user = models.ForeignKey(User)
    description = models.TextField('Event description', null=True)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)
    periodic = models.BooleanField(default=False)
    period = models.DateTimeField(null=True)
    next_notification = models.DateTimeField(null=True)


class EventMediaInfo(models.Model):
    event = models.ForeignKey(Event)
    media = models.FileField(null=True)


class EventLabel(models.Model):
    event = models.ForeignKey(Event)
    label = models.CharField(max_length=100)
