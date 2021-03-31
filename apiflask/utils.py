from typing import Any

from werkzeug.http import HTTP_STATUS_CODES

_sentinel = object()


# TODO Remove these shortcuts when pin Flask>=2.0
def route_shortcuts(cls):
    """A decorator used to add route shortcuts for `Flask` and `Blueprint` objects.

    Includes `get()`, `post()`, `put()`, `patch()`, `delete()`.

    Examples:

    ```python
    from flask import Flask

    @route_shortcuts
    class APIFlask(Flask):
        pass

    app = APIFlask(__name__)

    @app.get('/')
    def hello():
        return 'Hello!'
    ```

    *Version added: 0.2.0*

    *Version changed: 0.3.0*
    *Turn base class into class decorator.*
    """
    cls_route = cls.route

    def get(self, rule: str, **options: Any):
        """Shortcut for `app.route()`.
        """
        return cls_route(self, rule, methods=['GET'], **options)

    def post(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['POST'])`.
        """
        return cls_route(self, rule, methods=['POST'], **options)

    def put(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PUT'])`.
        """
        return cls_route(self, rule, methods=['PUT'], **options)

    def patch(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PATCH'])`.
        """
        return cls_route(self, rule, methods=['PATCH'], **options)

    def delete(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['DELETE'])`.
        """
        return cls_route(self, rule, methods=['DELETE'], **options)

    cls.get = get
    cls.post = post
    cls.put = put
    cls.patch = patch
    cls.delete = delete
    return cls


def get_reason_phrase(status_code: int) -> str:
    """A helper function used to get the reason phrase of given status code.

    Arguments:
        status_code: A standard HTTP status code.
    """
    return HTTP_STATUS_CODES.get(status_code, 'Unknown error')
