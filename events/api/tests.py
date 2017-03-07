import json

from django.urls.base import reverse
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from events.models import Label
from ..models import Event, EventStatus, EventMedia, EVENT_STATUSES


def dict_contains(parent, child):
    for key in child:
        if child[key] != parent[key]:
            return False
    return True


class EventTests(TestCase):

    def setUp(self):

        statuses = (EventStatus(status=s) for s in EVENT_STATUSES)
        EventStatus.objects.bulk_create(statuses)

        self.sample_payload = {
          "description": "We are number one",
          "start": "1997-08-06 23:12:12",
          "status": "W",
          "end": "1997-08-06 23:12:13"
        }

        self.sample_payload_with_labels = dict(labels=["a", "b"], **self.sample_payload.copy())

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
        users = User.objects.all()
        events = Event.objects.filter(user__in=users)
        Label.objects.filter(events=events).delete()
        events.delete()
        users.delete()

    def auth(self, username=None):
        create_payload = self.user_create_payload.copy()
        login_payload = self.user_login_payload.copy()

        if username:
            for payload in [create_payload, login_payload]:
                payload['username'] = username

        self.client.post(reverse('users:user_register'), create_payload)
        self.client.post(reverse('auth'), login_payload)

    @staticmethod
    def reformat_date(datum):
        return datetime.strptime(datum, '%Y-%m-%d %H:%M:%S')\
            .strftime('%Y-%m-%dT%H:%M:%SZ')

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

    def test_privacy(self):
        self.auth()
        self.client.post(reverse('events:event_create'), self.sample_payload_with_labels)

        response = self.client.get(reverse('events:event_list'))

        first_user_data = response.json()['data']

        self.auth(username='alex1@gmail.com')

        response = self.client.get(reverse('events:event_list'))

        self.assertNotEqual(len(response.json()['data']), first_user_data)

    def test_send_file(self):
        self.auth()
        payload = self.sample_payload_with_labels.copy()
        payload['media'] = open('img.jpg', 'rb')
        response = self.client.post(reverse('events:event_create'), payload)

        event_id = response.data['data']['id']

        self.assertEquals(EventMedia.objects.first().event_id, event_id)

    def test_event_update(self):
        self.auth()
        payload = self.sample_payload.copy()

        response = self.client.post(reverse('events:event_create'), payload)

        event_id = response.data['data']['id']

        payload["description"] = "new_description"
        payload["periodic"] = True
        payload["period"] = "30 00:00:00"
        payload["end"] = payload["start"]
        payload["status"] = "C"
        payload["place"] = "place"

        encoded_request = bytes(json.dumps(payload), encoding='utf-8')

        self.client.patch(reverse('events:event_update', args=(event_id,)),
                          data=encoded_request, content_type="application/json")

        response = self.client.get(reverse('events:event_detail', args=(event_id,)))
        payload['start'], payload['end'] = list(map(self.reformat_date,
                                                    (payload['start'], payload['end'])
                                                    )
                                                )

        self.assertTrue(dict_contains(response.data['data'], payload))

    def test_update_not_found(self):
        self.auth()

        encoded_request = bytes(json.dumps(self.sample_payload_with_labels), encoding='utf-8')

        response = self.client.patch(reverse('events:event_update', args=(0,)),
                          data=encoded_request, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_wrong_format(self):
        self.auth()

        response = self.client.post(reverse('events:event_create'), self.sample_payload_with_labels)

        event_id = response.data['data']['id']

        payload = self.sample_payload_with_labels.copy()
        payload['start'] = payload['end'] = 'nothing good'

        encoded_request = bytes(json.dumps(payload), encoding='utf-8')

        response = self.client.patch(reverse('events:event_update', args=(event_id,)),
                                     data=encoded_request, content_type='application/json')

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_error(self):
        self.auth()
        payload = self.sample_payload_with_labels.copy()
        payload['start'] = 'wrong_date format'
        response = self.client.post(reverse('events:event_create'), payload)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_period_without_periodic_flag_error(self):
        self.auth()
        payload = self.sample_payload_with_labels.copy()
        payload['period'] = "00:10:00"
        payload['periodic'] = False

        response = self.client.post(reverse('events:event_create'), payload)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_error_creating_overlapping_events(self):
        self.auth()
        payload = self.sample_payload_with_labels.copy()

        self.client.post(reverse('events:event_create'), payload)

        response = self.client.post(reverse('events:event_create'), payload)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
