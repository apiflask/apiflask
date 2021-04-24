from typing import Any

from flask.views import MethodViewType

from .openapi import default_response
from .openapi import get_summary_from_view_func
from .openapi import get_description_from_view_func


def route_patch(cls):
    """Support to use @app.route on a MethodView class."""
    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', f.__name__.lower())
            if isinstance(f, MethodViewType):
                # MethodView class
                view_func = f.as_view(endpoint)
                if self.enable_openapi:
                    view_func._method_spec = {}
                    for method_name in f.methods:  # method_name: ['GET', 'POST', ...]
                        method = f.__dict__[method_name.lower()]
                        if not hasattr(method, '_spec'):
                            if not self.config['AUTO_200_RESPONSE']:
                                continue
                            method._spec = {'response': default_response}
                        if not method._spec.get('summary') and self.config['AUTO_PATH_SUMMARY']:
                            method._spec['summary'] = get_summary_from_view_func(
                                method, f'{method_name.title()} {f.__name__}'
                            )
                        if not method._spec.get('description') and \
                           self.config['AUTO_PATH_DESCRIPTION']:
                            method._spec['description'] = get_description_from_view_func(method)
                        view_func._method_spec[method_name] = method._spec
            else:
                view_func = f
            self.add_url_rule(rule, endpoint, view_func, **options)
            return f
        return decorator

    cls.route = route
    return cls


# TODO Remove these shortcuts when pin Flask>=2.0
def route_shortcuts(cls):
    """A decorator to add route shortcuts for `Flask` and `Blueprint` objects.

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
    - Turn base class into class decorator.
    """
    cls_route = cls.route

    def get(self, rule: str, **options: Any):
        """Shortcut for `app.route()`."""
        return cls_route(self, rule, methods=['GET'], **options)

    def post(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['POST'])`."""
        return cls_route(self, rule, methods=['POST'], **options)

    def put(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PUT'])`."""
        return cls_route(self, rule, methods=['PUT'], **options)

    def patch(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PATCH'])`."""
        return cls_route(self, rule, methods=['PATCH'], **options)

    def delete(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['DELETE'])`."""
        return cls_route(self, rule, methods=['DELETE'], **options)

    cls.get = get
    cls.post = post
    cls.put = put
    cls.patch = patch
    cls.delete = delete
    return cls
