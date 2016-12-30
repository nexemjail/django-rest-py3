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
from serializers import (
    UserLoginSerializer,
    UserCreateSerializer,
    UserSerializer
)


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(User, pk=int(self.kwargs['id']))


class UserLoginAPIView(views.APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])
            if user:
                login(request, user)
                return response.Response({'detail': 'login successful'}, status.HTTP_200_OK)
            return response.Response({'detail': 'user not exist or invalid credentials'}, status.HTTP_403_FORBIDDEN)
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logout(request)
        return response.Response({'detail': 'log out was successful'}, status.HTTP_200_OK)


class UserCreateAPIView(generics.CreateAPIView):
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

