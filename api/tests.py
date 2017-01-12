from freezegun import freeze_time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django.test import Client
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


class ApiTestCase(TestCase):
    JWT_KEY = 'JWT '

    def setUp(self):
        self.client = Client()

        self.sample_user_payload = {
            "email": "alex228@gmail.com",
            "username": "alex228@gmail.com",
            "first_name": "Alex",
            "last_name":  "Sh",
            "password": "djangodjango",
            "password2": "djangodjango"
        }

    def tearDown(self):
        User.objects.filter(username=self.sample_user_payload['username']).delete()

    def test_registration(self):
        response = self.client.post('/register/',  self.sample_user_payload)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_already_exists(self):
        self.client.post('/register/',  self.sample_user_payload)
        response = self.client.post('/register/',  self.sample_user_payload)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_obtain_token(self):
        self.client.post('/register/', self.sample_user_payload)
        response = self.client.post('/login/', {
            'username': self.sample_user_payload['username'],
            'password': self.sample_user_payload['password']
        })
        self.assertTrue(bool(response.data.get('token', False)), True)

    def test_get_info(self):
        self.client.post('/register/', self.sample_user_payload)
        response = self.client.post('/login/', {
            'username': self.sample_user_payload['username'],
            'password': self.sample_user_payload['password']
        })
        token = response.data['token']

        user_id = User.objects.get(username=self.sample_user_payload['username']).id

        response = self.client.get('/{}/'.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token)

        self.assertIn('username', response.data['data'])

    def test_invalid_token(self):
        self.client.post('/register/', self.sample_user_payload)
        response = self.client.post('/login/', {
            'username': self.sample_user_payload['username'],
            'password': self.sample_user_payload['password']
        })
        token = response.data['token']

        user_id = User.objects.get(username=self.sample_user_payload['username']).id

        response = self.client.get('/{}/'.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token + 'seed')

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_expiration(self):

        now = datetime.now()
        self.client.post('/register/', self.sample_user_payload)
        response = self.client.post('/login/', {
            'username': self.sample_user_payload['username'],
            'password': self.sample_user_payload['password']
        })
        token = response.data['token']

        with freeze_time(now + timedelta(seconds=320)):
            user_id = User.objects.get(username=self.sample_user_payload['username']).id

            response = self.client.get('/{}/'.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token)

            self.assertEqual(response.status_code, 403)








