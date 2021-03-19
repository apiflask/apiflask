from flask import current_app
from werkzeug.http import HTTP_STATUS_CODES


class HTTPError(Exception):

    def __init__(self, status_code, message=None, detail=None, headers=None):
        super(HTTPError, self).__init__()
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        if message is not None:
            self.message = message
        else:
            self.message = get_error_message(status_code)


class ValidationError(HTTPError):
    pass


def abort(status_code, message=None, detail=None, headers=None):
    raise HTTPError(status_code, message, detail, headers)


def get_error_message(status_code):
    return HTTP_STATUS_CODES.get(status_code, 'Unknown error')


def default_error_handler(status_code, message=None, detail=None, headers=None):
    if message is None:
        message = get_error_message(status_code)
    if detail is None:
        detail = {}
    body = {'detail': detail, 'message': message, 'status_code': status_code}
    if headers is None:
        return body, status_code
    else:
        return body, status_code, headers
