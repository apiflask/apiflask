from flask import g, current_app
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .errors import default_error_handler


class _AuthBase:

    def __init__(self, description=None):
        self.description = description

    @property
    def current_user(self):
        if hasattr(g, 'flask_httpauth_user'):  # pragma: no cover
            return g.flask_httpauth_user


class _AuthErrorMixin:

    def __init__(self):
        @self.error_handler
        def handle_auth_error(status_code):
            if current_app.json_errors:
                return default_error_handler(status_code)
            else:
                return 'Unauthorized Access', status_code


class HTTPBasicAuth(_AuthBase, BaseHTTPBasicAuth, _AuthErrorMixin):

    def __init__(self, scheme=None, realm=None, description=None):
        super(HTTPBasicAuth, self).__init__(description=description)
        BaseHTTPBasicAuth.__init__(self, scheme=scheme, realm=realm)
        _AuthErrorMixin.__init__(self)


class HTTPTokenAuth(_AuthBase, BaseHTTPTokenAuth, _AuthErrorMixin):

    def __init__(self, scheme='Bearer', realm=None, header=None, description=None):
        super(HTTPTokenAuth, self).__init__(description=description)
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        _AuthErrorMixin.__init__(self)
