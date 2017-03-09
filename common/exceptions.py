class HttpNotFound404(Exception):
    status_code = 404
    message = 'Entity not found'
