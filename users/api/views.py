from django.contrib.auth.models import User
from rest_framework import (
    permissions,
    generics,
    status,
)

from common.auth import refresh_jwt
from common.utils import responsify
from users.api.serializers import (
    UserCreateSerializer,
    UserSerializer
)


class UserDetailAPIView(generics.RetrieveAPIView):
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
    @responsify
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user:
            serialized_user = self.serializer_class(user).data
            return serialized_user, status.HTTP_200_OK

        return 'User not found', status.HTTP_404_NOT_FOUND


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'

    @responsify
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # seems strange
            self.perform_create(serializer)
            user = serializer.instance

            return UserSerializer(instance=user).data, status.HTTP_201_CREATED, 'User created successfully'
        return serializer.errors, status.HTTP_400_BAD_REQUEST




