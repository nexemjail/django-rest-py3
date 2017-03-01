from django.conf.urls import url

from .views import (
    EventCreateAPIView,
    EventDetailAPIView,
    EventListAPIView
)

urlpatterns = [
    url(r'^event/create/$', EventCreateAPIView.as_view(), name='event_create'),
    url(r'^event/(?P<pk>[0-9]+)/$', EventDetailAPIView.as_view(), name='event_details'),
    url(r'^event/list/', EventListAPIView.as_view(), name='event_list')
]
