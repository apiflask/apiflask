from flask import g
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .exceptions import HTTPError


class _AuthBase:

    def __init__(self):
        @self.error_handler
        def handle_auth_error(status_code):
            raise HTTPError(status_code)

    @property
    def current_user(self):
        if hasattr(g, 'flask_httpauth_user'):
            return g.flask_httpauth_user


class HTTPBasicAuth(BaseHTTPBasicAuth, _AuthBase):

    def __init__(self, *args, **kwargs):
        super(HTTPBasicAuth, self).__init__(*args, **kwargs)
        _AuthBase.__init__(self)


class HTTPTokenAuth(BaseHTTPTokenAuth, _AuthBase):

    def __init__(self, *args, **kwargs):
        super(HTTPTokenAuth, self).__init__(*args, **kwargs)
        _AuthBase.__init__(self)
