from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView


class ObtainJSONWebToken(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super(ObtainJSONWebToken, self).post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            token = response.data.get('token')
            response.set_cookie('JWT', token)
        return response
