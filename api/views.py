from django.contrib.auth.models import User
from rest_framework import (
    permissions,
    generics,
    status,
    response
)
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from .utils import template_response

from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    EventSerializer,
    EventCreateSerializer
)


class JWTAuth(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        return request.QUERY_PARAMS.get('JWT')


class UserDetailAPIView(generics.RetrieveAPIView, JWTAuth):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = int(self.kwargs['id'])
        if pk < 0:
            return None
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user:
            serialized_user = self.serializer_class(user).data
            response_json = template_response(status='OK',
                                              code=status.HTTP_200_OK,
                                              message='Get object',
                                              data=serialized_user)
            return response.Response(response_json, status.HTTP_200_OK)

        response_json = template_response(status='Error',
                                          code=status.HTTP_404_NOT_FOUND,
                                          message='Object not found')
        return response.Response(response_json, status.HTTP_404_NOT_FOUND)


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # seems strange
            self.perform_create(serializer)
            user = serializer.instance

            response_json = template_response('User created',
                                              code=status.HTTP_201_CREATED,
                                              message='User created successfully',
                                              data=UserSerializer(instance=user).data)
            return response.Response(response_json, status.HTTP_201_CREATED)
        response_json = template_response('Error',
                                          code=status.HTTP_400_BAD_REQUEST,
                                          message='Error while creating a user',
                                          data=serializer.errors)
        return response.Response(
            response_json, status.HTTP_400_BAD_REQUEST)


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



