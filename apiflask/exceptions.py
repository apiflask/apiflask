from typing import Any, Optional, Mapping, Union, Tuple

from werkzeug.exceptions import default_exceptions

from .utils import get_reason_phrase


class HTTPError(Exception):
    """The exception used to end the request handling process and
    return an error response.

    Examples:

    ```python
    from apiflask import APIFlask, HTTPError
    from flask import escape

    app = APIFlask(__name__)

    @app.get('/<name>')
    def hello(name):
        if name == 'Foo':
            rasie HTTPError(404, 'This man is missing.')
        return f'Hello, escape{name}'!
    ```
    """

    def __init__(
        self,
        status_code: int,
        message: Optional[str] = None,
        detail: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None
    ) -> None:
        """
        Arguments:
            status_code: The status code of the error (4XX and 5xx).
            message: The simple description of the error. If not provided,
                the reason phrase of the status code will be used.
            detail: The detail information of the error, it can be used to
                provided addition information such as custom error code, documentation
                URL, etc.
            headers: A dict of headers used in error response.
        """
        super(HTTPError, self).__init__()
        if status_code not in default_exceptions:
            raise LookupError(
                f'No exception for status code "{status_code}",'
                ' valid error status code are "4XX" and "5XX".'
            )
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        if message is not None:
            self.message = message
        else:
            self.message = get_reason_phrase(status_code)


class ValidationError(HTTPError):
    """The exception used when request validation error happened.
    """
    pass


def abort_json(
    status_code: int,
    message: Optional[str] = None,
    detail: Optional[Any] = None,
    headers: Optional[Mapping[str, str]] = None
) -> None:
    """A quick version of HTTPError exception. Similar to Flask's `abort`,
    but return a JSON response.

    Examples:

    ```python
    from apiflask import APIFlask, abort_json
    from flask import escape

    app = APIFlask(__name__)

    @app.get('/<name>')
    def hello(name):
        if name == 'Foo':
            abort_json(404, 'This man is missing.')
        return f'Hello, escape{name}'!
    ```

    P.S. When `app.json_errors` is `True` (default), Flask's `abort` will also return
    JSON error response.

    Arguments:
        status_code: The status code of the error (4XX and 5xx).
        message: The simple description of the error. If not provided,
            the reason phrase of the status code will be used.
        detail: The detail information of the error, it can be used to
            provided addition information such as custom error code, documentation
            URL, etc.
        headers: A dict of headers used in error response.
    """
    raise HTTPError(status_code, message, detail, headers)


def default_error_handler(
    status_code: int,
    message: Optional[str] = None,
    detail: Optional[Any] = None,
    headers: Optional[Mapping[str, str]] = None
) -> Union[Tuple[dict, int], Tuple[dict, int, Mapping[str, str]]]:
    """The default error handler used in APIFlask.

    Arguments:
        status_code: The status code of the error (4XX and 5xx).
        message: The simple description of the error. If not provided,
            the reason phrase of the status code will be used.
        detail: The detail information of the error, it can be used to
            provided addition information such as custom error code, documentation
            URL, etc.
        headers: A dict of headers used in error response.
    """
    if message is None:
        message = get_reason_phrase(status_code)
    if detail is None:
        detail = {}
    body = {'detail': detail, 'message': message, 'status_code': status_code}
    if headers is None:
        return body, status_code
    else:
        return body, status_code, headers
