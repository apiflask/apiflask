from typing import Optional, Union, Tuple, Any, Mapping

from flask import g, current_app
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .errors import default_error_handler


class _AuthBase:

    def __init__(self, description: Optional[str] = None) -> None:
        self.description = description

    @property
    def current_user(self) -> Union[None, Any]:
        return g.get('flask_httpauth_user', None)


def handle_auth_error(
    status_code: int
) -> Union[Tuple[str, int], Tuple[dict, int], Tuple[dict, int, Mapping[str, str]]]:
    if current_app.json_errors:
        return default_error_handler(status_code)
    else:
        return 'Unauthorized Access', status_code


class HTTPBasicAuth(_AuthBase, BaseHTTPBasicAuth):

    def __init__(
        self,
        scheme=None,
        realm=None,
        description=None
    ) -> None:
        super(HTTPBasicAuth, self).__init__(description=description)
        BaseHTTPBasicAuth.__init__(self, scheme=scheme, realm=realm)
        self.error_handler(handle_auth_error)


class HTTPTokenAuth(_AuthBase, BaseHTTPTokenAuth):

    def __init__(
        self,
        scheme='Bearer',
        realm=None,
        header=None,
        description=None
    ) -> None:
        super(HTTPTokenAuth, self).__init__(description=description)
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        self.error_handler(handle_auth_error)
