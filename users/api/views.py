from django.contrib.auth.models import User
from rest_framework import (
    permissions,
    generics,
    status,
    response
)

from common.auth import JWTAuth, refresh_jwt
from common.utils import template_response
from users.api.serializers import (
    UserCreateSerializer,
    UserSerializer
)


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

    @refresh_jwt
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




