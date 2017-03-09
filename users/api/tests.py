from django.urls.base import reverse
from freezegun import freeze_time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django.test import Client
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from django.conf import settings


class ApiTestCase(TestCase):
    AUTH_URL = reverse('auth')
    REGISTER_URL = reverse('users:user_register')
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
        User.objects.all().delete()

    def authenticate(self, username=None):
        payload = self.sample_user_payload.copy()
        if username:
            payload['username'] = username

        return self.client.post(reverse('auth'), {
            'username': payload['username'],
            'password': payload['password']
        })

    def register(self, username=None, password=None):
        payload = self.sample_user_payload.copy()
        if username:
            payload['username'] = username
        if password:
            payload['password'] = password

        return self.client.post(reverse('users:user_register'),  payload)

    def get_user(self, user_created_response):
        response = self.client.get(
            reverse('users:user_detail', kwargs=dict(id=user_created_response.data['data']['id']))
        )
        return response

    def test_registration(self):
        response = self.register()

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_already_exists(self):
        self.register()
        response = self.register()

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_obtain_token(self):
        self.register()
        response = self.authenticate()

        self.assertTrue(bool(response.data.get('token')), True)

    def test_obtain_token_error(self):
        self.register(username='seed')
        response = self.authenticate()

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_not_authorized_error(self):
        response = self.register()
        self.authenticate()
        del self.client.cookies[settings.JWT_KEY]
        response = self.get_user(response)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_info(self):
        response = self.register()
        self.authenticate()

        response = self.get_user(response)

        self.assertIn('username', response.data['data'])

    def test_invalid_token(self):
        response = self.register()

        self.authenticate()
        self.client.cookies[settings.JWT_KEY] = 'invalid cookie'

        response = self.get_user(response)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_expiration(self):

        now = datetime.now()
        response = self.register()

        self.authenticate()

        with freeze_time(now + timedelta(seconds=1810)):

            response = self.get_user(response)

            self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_update_token(self):
        response_registration = self.register()

        response = self.authenticate()
        cookie = response.cookies.get(settings.JWT_KEY)

        # somehow signature is the same if executed fast enough
        with freeze_time(datetime.now() + timedelta(seconds=10)):
            response = self.get_user(response_registration)

            self.assertNotEqual(response.cookies.get(settings.JWT_KEY).value, cookie.value)
