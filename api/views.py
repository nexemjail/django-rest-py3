from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from rest_framework import (
    permissions,
    generics,
    views,
    status,
    response
)
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from .serializers import (
    UserLoginSerializer,
    UserCreateSerializer,
    UserSerializer
)


class UserDetailAPIView(generics.RetrieveAPIView, BaseJSONWebTokenAuthentication):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_jwt_value(self, request):
        return request.QUERY_PARAMS.get('jwt')

    def get_object(self):
        return get_object_or_404(User, pk=int(self.kwargs['id']))


class UserLoginAPIView(views.APIView, BaseJSONWebTokenAuthentication):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def get_jwt_value(self, request):
        return request.QUERY_PARAMS.get('jwt')

    def post(self, request):
        if request.user:
            login(request, request.user)
            return response.Response({'detail': 'login successful'}, status.HTTP_200_OK)
        return response.Response({'detail': 'user not exist or invalid credentials'}, status.HTTP_403_FORBIDDEN)


class UserLogoutAPIView(generics.RetrieveAPIView, BaseJSONWebTokenAuthentication):
    permission_classes = [permissions.IsAuthenticated]

    def get_jwt_value(self, request):
        return request.QUERY_PARAMS.get('jwt')

    def get(self, request):
        logout(request)
        return response.Response({'detail': 'log out was successful'}, status.HTTP_200_OK)


class UserCreateAPIView(generics.CreateAPIView, BaseJSONWebTokenAuthentication):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # seems strange
            if User.objects.filter(username=serializer.validated_data['username']).exists():
                return response.Response({'detail': 'user already exists'}, status.HTTP_409_CONFLICT)
            self.perform_create(serializer)
            return response.Response({'detail': 'user created'}, status.HTTP_201_CREATED)
        return response.Response({'detail': 'invalid data format'}, status.HTTP_400_BAD_REQUEST)

