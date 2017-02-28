from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token

from .views import (
    UserCreateAPIView,
    UserDetailAPIView,
EventCreateAPIView
)

api_patterns = [
    url(r'^(?P<id>[0-9]+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^event/create/$', EventCreateAPIView.as_view(), name='create_event'),
]

urlpatterns = [
    url(r'^auth/$', obtain_jwt_token, name='auth'),
    url(r'^', include(api_patterns)),
]
