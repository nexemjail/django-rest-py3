from rest_framework import generics, response, status, permissions

from django_filters.rest_framework import DjangoFilterBackend
from common.auth import JWTAuth, refresh_jwt
from common.permissions import IsAuthoredBy, IsMediaAuthoredBy
from common.utils import template_response
from events.models import EventMedia

from .serializers import EventCreateSerializer, EventSerializer, EventMediaSerializer
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
                 EventSerializer(instance=obj, context=dict(request=self.request)).data
            )
        else:
            response_json = template_response(
                'Error',
                status.HTTP_400_BAD_REQUEST,
                message='Invalid data',
                data=serializer.errors
            )
        return response.Response(response_json, status=response_json['code'])


class EventDetailAPIView(generics.RetrieveUpdateAPIView, JWTAuth):
    serializer_class = EventSerializer
    permission_classes = [IsAuthoredBy]
    queryset = Event

    @refresh_jwt
    def retrieve(self, request, *args, **kwargs):
        response = super(EventDetailAPIView, self).retrieve(request, *args, **kwargs)
        response.data = template_response(code=response.status_code, data=response.data)
        return response

    @refresh_jwt
    def patch(self, request, *args, **kwargs):
        response = super(EventDetailAPIView, self).patch(request, *args, **kwargs)
        response.data = template_response(code=response.status_code, data=response.data)
        return response


class EventMediaDetailAPIView(generics.RetrieveAPIView, JWTAuth):
    serializer_class = EventMediaSerializer
    permission_classes = [IsMediaAuthoredBy]
    queryset = EventMedia.objects.all()

    @refresh_jwt
    def retrieve(self, request, *args, **kwargs):
        response = super(EventMediaDetailAPIView, self).retrieve(request, *args, **kwargs)
        response.data = template_response(code=response.status_code, data=response.data)
        return response


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
        return Event.objects.filter(user=self.request.user).select_related('status').prefetch_related('labels', 'media')
