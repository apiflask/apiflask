from flask import g
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .exceptions import HTTPError


class _AuthBase:

    def __init__(self, description=None):
        self.description = description

        @self.error_handler
        def handle_auth_error(status_code):
            raise HTTPError(status_code)

    @property
    def current_user(self):
        if hasattr(g, 'flask_httpauth_user'):  # pragma: no cover
            return g.flask_httpauth_user


class HTTPBasicAuth(BaseHTTPBasicAuth, _AuthBase):

    def __init__(self, scheme=None, realm=None, description=None):
        super(HTTPBasicAuth, self).__init__(scheme=scheme, realm=realm)
        _AuthBase.__init__(self, description=description)


class HTTPTokenAuth(BaseHTTPTokenAuth, _AuthBase):

    def __init__(self, scheme='Bearer', realm=None, header=None, description=None):
        super(HTTPTokenAuth, self).__init__(scheme=scheme, realm=realm, header=header)
        _AuthBase.__init__(self, description=description)
