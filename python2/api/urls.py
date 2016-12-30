from django.conf.urls import url, include
from rest_framework import urls
from rest_framework.authtoken.views import obtain_auth_token
from views import (
    UserCreateAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserDetailAPIView,
)

api_patterns = [
    url(r'^(?P<id>[0-9]+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'),
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^logout/$', UserLogoutAPIView.as_view(), name='logout'),
]

urlpatterns = [
    # url(r'^api-token/$', obtain_auth_token),
    url(r'^auth/', include(urls, namespace='rest_framework')),
    url(r'^', include(api_patterns)),

]