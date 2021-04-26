from typing import Any

from flask.views import MethodViewType

from .openapi import get_summary_from_view_func
from .openapi import get_description_from_view_func


def route_patch(cls):
    """Support to use the `route` decorator on a MethodView class.

    *Version Added: 0.5.0*
    """
    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', f.__name__.lower())
            if isinstance(f, MethodViewType):
                # MethodView class
                if 'methods' in options:
                    raise RuntimeError(
                        'Use the "route" decorator without passing the "methods" '
                        'argument for "MethodView" classes.'
                    )
                view_func = f.as_view(endpoint)
                if self.enable_openapi:
                    view_func._method_spec = {}
                    view_func._spec = {}
                    for method_name in f.methods:  # method_name: ['GET', 'POST', ...]
                        method = f.__dict__[method_name.lower()]
                        if not hasattr(method, '_spec'):
                            method._spec = {'no_spec': True}
                        if not method._spec.get('summary'):
                            method._spec['summary'] = get_summary_from_view_func(
                                method, f'{method_name.title()} {f.__name__}'
                            )
                            method._spec['generated_summary'] = True
                        if not method._spec.get('description'):
                            method._spec['description'] = get_description_from_view_func(method)
                            method._spec['generated_description'] = True
                        view_func._method_spec[method_name] = method._spec
            else:
                view_func = f
            self.add_url_rule(rule, endpoint, view_func, **options)
            return f
        return decorator

    cls.route = route
    return cls


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

    def _method_route(self, method: str, rule: str, options: Any):
        if 'methods' in options:
            raise RuntimeError('Use the "route" decorator to use the "methods" argument.')

        def decorator(f):
            if isinstance(f, MethodViewType):
                raise RuntimeError(
                        'The route shortcuts cannot be used with "MethodView" classes, '
                        'use "route" decorator instead.'
                    )
            return cls_route(self, rule, methods=[method], **options)(f)
        return decorator

    def get(self, rule: str, **options: Any):
        """Shortcut for `app.route()`."""
        return _method_route(self, 'GET', rule, options)

    def post(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['POST'])`."""
        return _method_route(self, 'POST', rule, options)

    def put(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PUT'])`."""
        return _method_route(self, 'PUT', rule, options)

    def patch(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['PATCH'])`."""
        return _method_route(self, 'PATCH', rule, options)

    def delete(self, rule: str, **options: Any):
        """Shortcut for `app.route(methods=['DELETE'])`."""
        return _method_route(self, 'DELETE', rule, options)

    cls.get = get
    cls.post = post
    cls.put = put
    cls.patch = patch
    cls.delete = delete
    return cls
