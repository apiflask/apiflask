_sentinel = object()


class Scaffold:
    """Base object for APIFlask and Blueprint.

    .. versionadded:: 0.2.0
    """
    # TODO Remove these shortcuts when pin Flask>=2.0
    def get(self, rule, **options):
        """Shortcut for ``app.route()``.

        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['GET'], **options)

    def post(self, rule, **options):
        """Shortcut for ``app.route(methods=['POST'])``.

        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['POST'], **options)

    def put(self, rule, **options):
        """Shortcut for ``app.route(methods=['PUT'])``.

        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['PUT'], **options)

    def patch(self, rule, **options):
        """Shortcut for ``app.route(methods=['PATCH'])``.

        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['PATCH'], **options)

    def delete(self, rule, **options):
        """Shortcut for ``app.route(methods=['DELETE'])``.

        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['DELETE'], **options)
