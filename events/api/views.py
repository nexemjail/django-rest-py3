from rest_framework import generics, response, status, permissions

from django_filters.rest_framework import DjangoFilterBackend
from common.auth import JWTAuth, refresh_jwt
from common.permissions import IsAuthoredBy
from common.utils import template_response

from .serializers import EventCreateSerializer, EventSerializer
from ..models import Event
from .filters import EventListFilter


class EventCreateAPIView(generics.CreateAPIView, JWTAuth):
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @refresh_jwt
    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=False):
            obj = serializer.save(user=self.request.user)
            response_json = template_response(
                'Created',
                 status.HTTP_201_CREATED,
                 'Event created',
                 EventSerializer(instance=obj).data
            )
        else:
            response_json = template_response(
                'Error',
                status.HTTP_400_BAD_REQUEST,
                message='Invalid data',
                data=serializer.errors
            )
        return response.Response(response_json)


class EventDetailAPIView(generics.RetrieveAPIView, JWTAuth):
    serializer_class = EventSerializer
    permission_classes = [IsAuthoredBy]
    queryset = Event

    @refresh_jwt
    def retrieve(self, request, *args, **kwargs):
        return super(EventDetailAPIView, self).retrieve(request, *args, **kwargs)


class EventUpdateAPIView(generics.UpdateAPIView, JWTAuth):

    @refresh_jwt
    def update(self, request, *args, **kwargs):
        pass


class EventListAPIView(generics.ListAPIView, JWTAuth):
    serializer_class = EventSerializer
    permission_classes = [IsAuthoredBy]
    filter_backends = [DjangoFilterBackend]
    filter_class = EventListFilter

    @refresh_jwt
    def list(self, request, *args, **kwargs):
        response = super(EventListAPIView, self).list(request, *args, **kwargs)
        response.data = template_response(status=response.status_text, code=response.status_code,
                                          message="", data=response.data)
        return response

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).select_related('status').prefetch_related('labels')
