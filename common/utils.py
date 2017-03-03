def template_response(status=None, code=None, message=None, data=None):
    return {
        'status': status,
        'code': code,
        'message': message,
        'data': data
    }
