from django.conf.urls import url

from .views import (
    EventCreateAPIView,
    EventDetailAPIView
)

urlpatterns = [
    url(r'^event/create/$', EventCreateAPIView.as_view(), name='create_event'),
    url(r'^event/(?P<pk>[0-9]+)/$', EventDetailAPIView.as_view(), name='event_detail'),
]
