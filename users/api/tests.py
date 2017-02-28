from django.urls.base import reverse
from freezegun import freeze_time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django.test import Client
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


class ApiTestCase(TestCase):
    JWT_KEY = 'JWT '
    AUTH_URL = '/auth/'
    REGISTER_URL = '/users/user/register/'
    USER_PATH = '/users/user/{}/'

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

    def _get_auth_response(self):
        return self.client.post(self.AUTH_URL, {
            'username': self.sample_user_payload['username'],
            'password': self.sample_user_payload['password']
        })

    def test_registration(self):
        response = self.client.post(self.REGISTER_URL,  self.sample_user_payload)

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_already_exists(self):
        self.client.post(self.REGISTER_URL,  self.sample_user_payload)

        response = self.client.post(self.REGISTER_URL, self.sample_user_payload)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_obtain_token(self):
        self.client.post(self.REGISTER_URL, self.sample_user_payload)
        response = self._get_auth_response()

        self.assertTrue(bool(response.data.get('token')), True)

    def test_obtain_token_error(self):
        payload = self.sample_user_payload.copy()
        payload['username'] = 'seed'

        self.client.post(self.REGISTER_URL, payload)
        response = self._get_auth_response()
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_info(self):
        response = self.client.post(self.REGISTER_URL, self.sample_user_payload)

        user_id = response.data.get('data').get('id')

        response = self._get_auth_response()
        token = response.data.get('token')

        response = self.client.get(self.USER_PATH.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token)

        self.assertIn('username', response.data['data'])

    def test_invalid_token(self):
        response = self.client.post(self.REGISTER_URL, self.sample_user_payload)

        user_id = response.data.get('data').get('id')

        response = self._get_auth_response()
        token = response.data['token']

        response = self.client.get(self.USER_PATH.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token + 'seed')

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_expiration(self):

        now = datetime.now()
        response = self.client.post(self.REGISTER_URL, self.sample_user_payload)

        user_id = response.data.get('data').get('id')

        response = self._get_auth_response()
        token = response.data['token']

        with freeze_time(now + timedelta(seconds=320)):

            response = self.client.get(self.USER_PATH.format(user_id), HTTP_AUTHORIZATION=self.JWT_KEY + token)

            self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
