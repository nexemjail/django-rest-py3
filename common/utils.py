from functools import wraps
from rest_framework import status
from rest_framework.response import Response


def template_response(data=None, code=status.HTTP_200_OK, message=None):
    return Response({
        'status_code': code,
        'data': data,
        'message': message,
    }, status=code)


def responsify(function):
    @wraps(function)
    def inner(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            if isinstance(result, dict) or isinstance(result, str):
                return template_response(result)
            elif isinstance(result, tuple):
                return template_response(*result)
            elif isinstance(result, Response):
                return template_response(data=result.data, code=result.status_code)
            return template_response()
        except BaseException as e:
            return template_response(data=e.message if hasattr(e, 'message') else str(e),
                                     code=e.status_code if hasattr(e, 'status_code')
                                        else status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     message='Error')
    return inner
