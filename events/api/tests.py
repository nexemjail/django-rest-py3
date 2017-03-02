from django.urls.base import reverse
from freezegun import freeze_time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django.test import Client
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from events.models import Label
from ..models import Event, EventStatus, EventMedia, EVENT_STATUSES


def dict_contains(parent, child):
    for key in child:
        if not child[key] == parent[key]:
            return False
    return True


class EventTests(TestCase):

    def setUp(self):

        statuses = (EventStatus(status=s) for s in EVENT_STATUSES)
        EventStatus.objects.bulk_create(statuses)

        self.sample_payload = {
          "description": "We are number one",
          "start": "1997-08-06 23:12:12",
          "status": "W"
        }

        self.user_create_payload = {
            "email": "alex@gmail.com",
            "username": "alex@gmail.com",
            "first_name": "Alex",
            "last_name": "Shlemenkov",
            "password": "password",
            "password2": "password"
        }

        self.user_login_payload = {
          "username": "alex@gmail.com",
          "password": "password"
        }

    def tearDown(self):
        user = User.objects.filter(username=self.user_login_payload['username']).first()
        events = Event.objects.filter(user=user)
        Label.objects.filter(events=events).delete()
        events.delete()
        user.delete()

    def auth(self):
        self.client.post(reverse('users:user_register'), self.user_create_payload)
        self.client.post(reverse('auth'), self.user_login_payload)

    def test_create_event(self):
        self.auth()
        response = self.client.post(reverse('events:event_create'), self.sample_payload)
        start_time = datetime.strptime(self.sample_payload['start'], '%Y-%m-%d %H:%M:%S')\
            .strftime('%Y-%m-%dT%H:%M:%SZ')

        expected_response = {
            'description': self.sample_payload['description'],
            'status': self.sample_payload['status'],
            'start': start_time,
            'user': self.user_login_payload['username']
        }

        self.assertTrue(dict_contains(response.data['data'], expected_response))

    def test_create_event_with_non_existent_labels(self):
        self.auth()

        payload = self.sample_payload.copy()
        labels = ['a', 'b']
        payload['labels'] = labels

        self.client.post(reverse('events:event_create'), payload)

        self.assertEquals(Label.objects.filter(name__in=labels).count(), len(labels))





