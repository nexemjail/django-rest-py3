from django.conf.urls import url, include
from rest_framework import urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from .views import (
    UserCreateAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserDetailAPIView,
)

api_patterns = [
    url(r'^(?P<id>[0-9]+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^login/$', obtain_jwt_token, name='login'),
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^logout/$', UserLogoutAPIView.as_view(), name='logout'),
]

urlpatterns = [
    url(r'^auth/', include(urls, namespace='rest_framework')),
    url(r'^', include(api_patterns)),

]