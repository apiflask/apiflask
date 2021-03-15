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
            self.message = HTTP_STATUS_CODES.get(
                status_code,
                current_app.config['UNKNOWN_ERROR_MESSAGE']
            )


class ValidationError(HTTPError):
    pass


def abort(status_code, message=None, detail=None, headers=None):
    raise HTTPError(status_code, message, detail, headers)
