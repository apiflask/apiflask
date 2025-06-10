from __future__ import annotations

import typing as t

from flask import current_app
from flask import g
from flask_httpauth import HTTPBasicAuth as BaseHTTPBasicAuth
from flask_httpauth import HTTPTokenAuth as BaseHTTPTokenAuth

from .exceptions import HTTPError
from .types import ErrorCallbackType
from .types import ResponseReturnValueType
from .types import SecuritySchema


class _AuthBase:
    """Base class for `HTTPBasicAuth` and `HTTPBasicAuth`."""

    def __init__(
        self,
        description: str | None = None,
        security_scheme_name: str | None = None,
    ) -> None:
        self.description = description
        self.security_scheme_name = security_scheme_name
        self.error_handler(self._auth_error_handler)  # type: ignore

    @property
    def current_user(self) -> None | t.Any:
        return g.get('flask_httpauth_user', None)

    @staticmethod
    def _auth_error_handler(status_code: int) -> ResponseReturnValueType:
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

    def error_processor(self, f: ErrorCallbackType) -> None:
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


class HTTPBasicAuth(_AuthBase, BaseHTTPBasicAuth, SecuritySchema):
    """Flask-HTTPAuth's HTTPBasicAuth with some modifications.

    - Add an authentication error handler that returns JSON response.
    - Expose the `auth.current_user` as a property.
    - Add a `description` attribute for OpenAPI Spec.
    - Add a `name` attribute for OpenAPI Spec.
    - Add the `get_security_schema` method for OpenAPI Spec.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPBasicAuth

    app = APIFlask(__name__)
    auth = HTTPBasicAuth()
    ```

    *Version changed: 2.4.1*

    - Add parameter `name`.

    *Version changed: 1.3.0*

    - Add `security_scheme_name` parameter.
    """

    def __init__(
        self,
        name: str = 'BasicAuth',
        scheme: str = 'Basic',
        realm: str | None = None,
        description: str | None = None,
        security_scheme_name: str | None = None,
    ) -> None:
        """Initialize an `HTTPBasicAuth` object.

        Arguments:
            name: The security scheme name, default to `BasicAuth`.
            scheme: The authentication scheme used in the `WWW-Authenticate`
                header. Defaults to `'Basic'`.
            realm: The realm used in the `WWW-Authenticate` header to indicate
                a scope of protection, defaults to use `'Authentication Required'`.
            description: The description of the OpenAPI security scheme.
            security_scheme_name: The name of the OpenAPI security scheme, default to `BasicAuth`.
        """
        BaseHTTPBasicAuth.__init__(self, scheme=scheme, realm=realm)
        super().__init__(description=description, security_scheme_name=security_scheme_name)
        self.name = security_scheme_name or name

    def get_security_schema(self) -> dict[str, t.Any]:
        security_schema = {
            'type': 'http',
            'scheme': 'basic',
        }

        if self.description is not None:
            security_schema['description'] = self.description

        return security_schema


class HTTPTokenAuth(_AuthBase, BaseHTTPTokenAuth, SecuritySchema):
    """Flask-HTTPAuth's HTTPTokenAuth with some modifications.

    - Add an authentication error handler that returns JSON response.
    - Expose the `auth.current_user` as a property.
    - Add a `description` attribute for OpenAPI Spec.
    - Add a `name` attribute for OpenAPI Spec.
    - Add the `get_security_schema` method for OpenAPI Spec.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPTokenAuth

    app = APIFlask(__name__)
    auth = HTTPTokenAuth()
    ```
    """

    def __init__(
        self,
        name: str = 'BearerAuth',
        scheme: str = 'Bearer',
        realm: str | None = None,
        header: str | None = None,
        description: str | None = None,
        security_scheme_name: str | None = None,
    ) -> None:
        """Initialize a `HTTPTokenAuth` object.

        Arguments:
            name: The security scheme name, default to `BearerAuth`.
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

            description: The description of the OpenAPI security scheme.
            security_scheme_name: The name of the OpenAPI security scheme,
                defaults to `BearerAuth` or `ApiKeyAuth`.

        *Version changed: 2.4.1*

        - Add parameter `name`.

        *Version changed: 1.3.0*

        - Add `security_scheme_name` parameter.
        """
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        super().__init__(description=description, security_scheme_name=security_scheme_name)
        self.name = security_scheme_name or name

    def get_security_schema(self) -> dict[str, t.Any]:
        security_schema = {
            'type': 'http',
            'scheme': 'bearer',
        }

        if self.description is not None:
            security_schema['description'] = self.description

        return security_schema


class HTTPAPIKeyAuth(_AuthBase, BaseHTTPTokenAuth, SecuritySchema):
    """Flask-HTTPAuth's HTTPTokenAuth with some modifications to implement APIKey authentication.

    - Add an authentication error handler that returns JSON response.
    - Expose the `auth.current_user` as a property.
    - Add a `description` attribute for OpenAPI Spec.
    - Add a `name` attribute for OpenAPI Spec.
    - Add the `get_security_schema` method for OpenAPI Spec.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPAPIKeyAuth

    app = APIFlask(__name__)
    auth = HTTPAPIKeyAuth()
    ```
    """

    def __init__(
        self,
        name: str = 'ApiKeyAuth',
        scheme: str = 'ApiKey',
        realm: str | None = None,
        header: str | None = 'X-API-Key',
        description: str | None = None,
        security_scheme_name: str | None = None,
    ) -> None:
        """Initialize a `HTTPAPIKeyAuth` object.

        Arguments:
            name: The security scheme name, default to `ApiKeyAuth`.
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

            description: The description of the OpenAPI security scheme.
            security_scheme_name: The name of the OpenAPI security scheme,
                defaults to `BearerAuth` or `ApiKeyAuth`.

        *Version changed: 2.4.1*

        - Add parameter `name`.

        *Version changed: 1.3.0*

        - Add `security_scheme_name` parameter.
        """
        BaseHTTPTokenAuth.__init__(self, scheme=scheme, realm=realm, header=header)
        super().__init__(description=description, security_scheme_name=security_scheme_name)
        self.name = security_scheme_name or name

    def get_security_schema(self) -> dict[str, t.Any]:
        security_schema = {
            'type': 'apiKey',
            'name': self.header,
            'in': 'header',
        }

        if self.description is not None:
            security_schema['description'] = self.description

        return security_schema
