from rest_framework import generics, status, permissions

from django_filters.rest_framework import DjangoFilterBackend
from common.auth import refresh_jwt
from common.exceptions import HttpNotFound404
from common.permissions import IsAuthoredBy, IsMediaAuthoredBy
from common.utils import responsify
from events.models import EventMedia

from .serializers import EventCreateSerializer, EventSerializer, EventMediaSerializer
from ..models import Event
from .filters import EventListFilter


class EventCreateAPIView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @refresh_jwt
    @responsify
    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context=dict(request=self.request))
        if serializer.is_valid(raise_exception=False):
            obj = serializer.save(user=self.request.user)
            return EventSerializer(instance=obj, context=dict(request=self.request)).data, \
                   status.HTTP_201_CREATED, 'Event created'
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST


class EventDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthoredBy]
    queryset = Event

    def get_object(self):
        try:
            return Event.objects.get(pk=self.kwargs.get('pk'))
        except Event.DoesNotExist:
            raise HttpNotFound404

    @refresh_jwt
    @responsify
    def retrieve(self, request, *args, **kwargs):
        return super(EventDetailAPIView, self).retrieve(request, *args, **kwargs)

    @refresh_jwt
    @responsify
    def patch(self, request, *args, **kwargs):
        return super(EventDetailAPIView, self).patch(request, *args, **kwargs)


class EventMediaDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EventMediaSerializer
    permission_classes = [IsMediaAuthoredBy]
    queryset = EventMedia.objects.all()

    @refresh_jwt
    @responsify
    def retrieve(self, request, *args, **kwargs):
        return super(EventMediaDetailAPIView, self).retrieve(request, *args, **kwargs)


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthoredBy]
    filter_backends = [DjangoFilterBackend]
    filter_class = EventListFilter

    @refresh_jwt
    @responsify
    def list(self, request, *args, **kwargs):
        return super(EventListAPIView, self).list(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).select_related('status').prefetch_related('labels', 'media')
