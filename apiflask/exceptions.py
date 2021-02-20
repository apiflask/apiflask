from werkzeug.exceptions import default_exceptions

class APIException(Exception):
    def __init__(self, status_code, detail=None, headers=None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        if detail is None:
            if status_code in default_exceptions:
                self.detail = default_exceptions[status_code].description
            else:
                self.detail = 'Unknown error'


class ValidationError(APIException):
    pass
