from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (
    permissions,
    generics,
    views,
    status,
    response
)
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .utils import template_response

from .serializers import (
    UserLoginSerializer,
    UserCreateSerializer,
    UserSerializer
)


class JWTAuth(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        return request.QUERY_PARAMS.get('jwt')


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


@method_decorator(csrf_exempt, name='post')
class UserLoginAPIView(views.APIView):
    serializer_class = JSONWebTokenSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            token, user = serializer.validated_data
            if request.user:
                response_json = template_response('OK',
                                                  code=status.HTTP_200_OK,
                                                  message='Login successful',
                                                  data=token)
                return response.Response(response_json, status.HTTP_200_OK)
        response_json = template_response('Request Error',
                                          code=status.HTTP_403_FORBIDDEN,
                                          message='Invalid credentials or user not exist')
        return response.Response(response_json, status.HTTP_403_FORBIDDEN)


class UserLogoutAPIView(generics.RetrieveAPIView, JWTAuth):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response_json = template_response('OK',
                                          code=status.HTTP_200_OK,
                                          message='Logout successful')
        return response.Response(response_json, status.HTTP_200_OK)


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # seems strange
            self.perform_create(serializer)

            response_json = template_response('User created',
                                              code=status.HTTP_201_CREATED,
                                              message='User created successful')
            return response.Response(response_json, status.HTTP_201_CREATED)
        response_json = template_response('Error',
                                          code=status.HTTP_400_BAD_REQUEST,
                                          message='User created successful',
                                          data=serializer.errors)
        return response.Response(
            response_json, status.HTTP_400_BAD_REQUEST)

