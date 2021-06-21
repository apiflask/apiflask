import typing as t

from flask import current_app
from flask import g
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .exceptions import _default_error_handler


class _AuthBase:
    """Base class for `HTTPBasicAuth` and `HTTPBasicAuth`."""

    def __init__(self, description: t.Optional[str] = None) -> None:
        self.description = description

    @property
    def current_user(self) -> t.Union[None, t.Any]:
        return g.get('flask_httpauth_user', None)


def handle_auth_error(
    status_code: int
) -> t.Union[t.Tuple[str, int], t.Tuple[dict, int], t.Tuple[dict, int, t.Mapping[str, str]]]:
    """The default error handler for Flask-HTTPAuth.

    This handler will return JSON response when `app.json_errors` is `True` (default).
    """
    if current_app.json_errors:  # type: ignore
        return _default_error_handler(status_code)
    return 'Unauthorized Access', status_code


class HTTPBasicAuth(_AuthBase, BaseHTTPBasicAuth):
    """Flask-HTTPAuth's HTTPBasicAuth with some modifications.

    - Add an authentication error handler that returns JSON response.
    - Expose the `auth.current_user` as a property.
    - Add a `description` attribute for OpenAPI Spec.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPBasicAuth

    app = APIFlask(__name__)
    auth = HTTPBasicAuth()
    ```
    """

    def __init__(
        self,
        scheme: str = 'Basic',
        realm: t.Optional[str] = None,
        description: t.Optional[str] = None
    ) -> None:
        """Initialize an `HTTPBasicAuth` object.

        Arguments:
            scheme: The authentication scheme used in the `WWW-Authenticate`
                header. Defaults to `'Basic'`.
            realm: The realm used in the `WWW-Authenticate` header to indicate
                a scope of protection, defaults to use `'Authentication Required'`.
            description: The description of the security scheme.
        """
        super().__init__(description=description)
        BaseHTTPBasicAuth.__init__(self, scheme=scheme, realm=realm)
        self.error_handler(handle_auth_error)


class HTTPTokenAuth(_AuthBase, BaseHTTPTokenAuth):
    """Flask-HTTPAuth's HTTPTokenAuth with some modifications.

    - Add an authentication error handler that returns JSON response.
    - Expose the `auth.current_user` as a property.
    - Add a `description` attribute for OpenAPI Spec.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPTokenAuth

    app = APIFlask(__name__)
    auth = HTTPTokenAuth()
    ```
    """

    def __init__(
        self,
        scheme: str = 'Bearer',
        realm: t.Optional[str] = None,
        header: t.Optional[str] = None,
        description: t.Optional[str] = None
    ) -> None:
        """Initialize a `HTTPTokenAuth` object.

        Arguments:
            scheme: The authentication scheme used in the `WWW-Authenticate`
                header. One of `'Bearer'` and `'ApiKey'`, defaults to `'Bearer'`.
            realm: The realm used in the `WWW-Authenticate` header to indicate
                 a scope of protection, defaults to use `'Authentication Required'`.
            header: The custom header where to obtain the token (instead
                of from `Authorization` header). If a custom header is used,
                the scheme should not be included. Example:

                ```
                X-API-Key: this-is-my-token
                ```

            description: The description of the security scheme.
        """
        super().__init__(description=description)
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        self.error_handler(handle_auth_error)
