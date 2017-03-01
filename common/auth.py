from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication


class JWTAuth(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        return request.COOKIES.get('JWT')
