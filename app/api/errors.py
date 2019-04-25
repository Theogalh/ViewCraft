from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def bad_request(message):
    """
    Return a 400 response with message.
    :param message: String to context the error.
    :return: Response object.
    """
    return error_response(400, message)


def error_response(status_code, message=None):
    """
    Return a response with message
    :param status_code: HTTP Status code in Integer.
    :param message: String to context the error.
    :return: Response object.
    """
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response
