from werkzeug.exceptions import default_exceptions
from flask import current_app


class HTTPError(Exception):
    status_code = None
    message = None
    detail = None
    headers = None

    def __init__(self, status_code=None, message=None, detail=None, headers=None):
        Exception.__init__(self)
        if status_code is not None:
            self.status_code = status_code
        if message is not None:
            self.message = message
        if detail is not None:
            self.detail = detail
        if headers is not None:
            self.headers = headers

        if self.message is None:
            if status_code in default_exceptions:
                self.message = default_exceptions[status_code].description
            else:
                self.message = current_app.config['UNKNOWN_ERROR_MESSAGE']


class ValidationError(HTTPError):
    pass


def abort(status_code, detail=None, headers=None):
    raise HTTPError(status_code, detail, headers)
