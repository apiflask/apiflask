from typing import Any

_sentinel = object()


def route_shortcuts(cls):
    cls_route = cls.route

    # TODO Remove these shortcuts when pin Flask>=2.0
    def get(self, rule: str, **options: Any):
        """Shortcut for ``app.route()``.

        .. versionadded:: 0.2.0
        """
        return cls_route(self, rule, methods=['GET'], **options)

    def post(self, rule: str, **options: Any):
        """Shortcut for ``app.route(methods=['POST'])``.

        .. versionadded:: 0.2.0
        """
        return cls_route(self, rule, methods=['POST'], **options)

    def put(self, rule: str, **options: Any):
        """Shortcut for ``app.route(methods=['PUT'])``.

        .. versionadded:: 0.2.0
        """
        return cls_route(self, rule, methods=['PUT'], **options)

    def patch(self, rule: str, **options: Any):
        """Shortcut for ``app.route(methods=['PATCH'])``.

        .. versionadded:: 0.2.0
        """
        return cls_route(self, rule, methods=['PATCH'], **options)

    def delete(self, rule: str, **options: Any):
        """Shortcut for ``app.route(methods=['DELETE'])``.

        .. versionadded:: 0.2.0
        """
        return cls_route(self, rule, methods=['DELETE'], **options)

    cls.get = get
    cls.post = post
    cls.put = put
    cls.patch = patch
    cls.delete = delete
    return cls
