import typing as t

from werkzeug.exceptions import default_exceptions

from .helpers import get_reason_phrase

_bad_schema_message = 'The schema must be a Marshmallow schema class or an OpenAPI schema dict.'


class HTTPError(Exception):
    """The exception to end the request handling and return an JSON error response.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPError
    from flask import escape

    app = APIFlask(__name__)

    @app.get('/<name>')
    def hello(name):
        if name == 'Foo':
            raise HTTPError(404, 'This man is missing.')
        return f'Hello, escape{name}'!
    ```
    """

    def __init__(
        self,
        status_code: int,
        message: t.Optional[str] = None,
        detail: t.Optional[t.Any] = None,
        headers: t.Optional[t.Mapping[str, str]] = None
    ) -> None:
        """Initialize the error response.

        Arguments:
            status_code: The status code of the error (4XX and 5xx).
            message: The simple description of the error. If not provided,
                the reason phrase of the status code will be used.
            detail: The detailed information of the error, you can use it to
                provide the addition information such as custom error code,
                documentation URL, etc.
            headers: A dict of headers used in the error response.

        *Version changed: 0.9.0*

        - Set `detail` and `headers` to empty dict if not set.
        """
        super().__init__()
        if status_code not in default_exceptions:
            raise LookupError(
                f'No exception for status code "{status_code}",'
                ' valid error status code are "4XX" and "5XX".'
            )
        self.status_code = status_code
        self.detail = detail or {}
        self.headers = headers or {}
        self.message = get_reason_phrase(status_code, 'Unknown error') \
            if message is None else message


class _ValidationError(HTTPError):
    """The exception used when the request validation error happened."""

    pass


def abort(
    status_code: int,
    message: t.Optional[str] = None,
    detail: t.Optional[t.Any] = None,
    headers: t.Optional[t.Mapping[str, str]] = None
) -> None:
    """A function to raise HTTPError exception.

    Similar to Flask's `abort`, but returns a JSON response.

    Examples:

    ```python
    from apiflask import APIFlask, abort
    from flask import escape

    app = APIFlask(__name__)

    @app.get('/<name>')
    def hello(name):
        if name == 'Foo':
            abort(404, 'This man is missing.')
        return f'Hello, escape{name}'!
    ```

    P.S. When `app.json_errors` is `True` (default), Flask's `flask.abort` will also
    return JSON error response.

    Arguments:
        status_code: The status code of the error (4XX and 5xx).
        message: The simple description of the error. If not provided,
            the reason phrase of the status code will be used.
        detail: The detailed information of the error, you can use it to
            provide the addition information such as custom error code,
            documentation URL, etc.
        headers: A dict of headers used in the error response.

    *Version changed: 0.4.0*

    - Rename the function name from `abort_json` to `abort`.
    """
    raise HTTPError(status_code, message, detail, headers)
