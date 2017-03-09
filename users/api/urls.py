from django.conf.urls import url

from .views import (
    UserCreateAPIView,
    UserDetailAPIView,
)

urlpatterns = [
    url(r'^user/(?P<id>[0-9]+)/$', UserDetailAPIView.as_view(), name='user_detail'),
    url(r'^user/register/$', UserCreateAPIView.as_view(), name='user_register'),
]
