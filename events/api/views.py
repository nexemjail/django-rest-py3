from rest_framework import generics, response, status, permissions

from common.auth import JWTAuth
from common.permissions import IsAuthoredBy
from common.utils import template_response

from .serializers import EventCreateSerializer, EventSerializer
from ..models import Event


class EventCreateAPIView(generics.CreateAPIView, JWTAuth):
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

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