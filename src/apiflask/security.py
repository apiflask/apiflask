import typing as t

from flask import current_app
from flask import g
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .exceptions import HTTPError
from .types import ErrorCallbackType
from .types import ResponseReturnValueType


class _AuthBase:
    """Base class for `HTTPBasicAuth` and `HTTPBasicAuth`."""

    def __init__(self, description: t.Optional[str] = None) -> None:
        self.description = description
        self.error_handler(self._auth_error_handler)  # type: ignore

    @property
    def current_user(self) -> t.Union[None, t.Any]:
        return g.get('flask_httpauth_user', None)

    @staticmethod
    def _auth_error_handler(
        status_code: int
    ) -> ResponseReturnValueType:
        """The default error handler for Flask-HTTPAuth.

        This handler will return JSON response when setting `APIFlask(json_errors=True)` (default).

        *Version changed: 0.9.0*

        - The default reason phrase is used for auth errors.
        - It will call the `app.error_callback` for auth errors.
        """
        error = HTTPError(status_code)
        if current_app.json_errors:  # type: ignore
            return current_app.error_callback(error)  # type: ignore
        return error.message, status_code  # type: ignore

    def error_processor(
        self,
        f: ErrorCallbackType
    ) -> None:
        """A decorator to register an error callback function for auth errors (401/403).

        The error callback function will be called when authentication errors happened.
        It should accept an `HTTPError` instance and return a valid response. APIFlask will pass
        the callback function you decorated to Flask-HTTPAuth's `error_handler` method internally.

        Example:

        ```python
        from apiflask import APIFlask, HTTPTokenAuth

        app = APIFlask(__name__)
        auth = HTTPTokenAuth()

        @auth.error_processor
        def my_auth_error_processor(error):
            return {
                'status_code': error.status_code,
                'message': error.message
            }, error.status_code
        ```

        See more details of the error object in
        [APIFlask.error_processor][apiflask.APIFlask.error_processor].

        *Version added: 0.9.0*
        """
        self.error_handler(lambda status_code: f(HTTPError(status_code)))  # type: ignore


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
        BaseHTTPBasicAuth.__init__(self, scheme=scheme, realm=realm)
        super().__init__(description=description)


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
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        super().__init__(description=description)
