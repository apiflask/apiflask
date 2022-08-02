import typing as t

from flask.views import MethodView

from .openapi import get_path_description
from .openapi import get_path_summary
from .types import ViewClassType
from .types import ViewFuncOrClassType
from .types import ViewFuncType


def route_patch(cls):
    """A decorator to add a patched `add_url_rule` method for `APIFlask` and
    `APIBlueprint` objects.

    The patched `add_url_rule` method will create a view function if passed a
    view class, and then generate spec from it.

    *Version changed: 0.10.0*

    - Remove the `route` decorator, and move the logic into `add_url_rule`.

    *Version added: 0.5.0*
    """
    def record_spec_for_view_class(
        view_func: ViewFuncType,
        view_class: ViewClassType
    ) -> ViewFuncType:
        # when the user call add_url_rule multiple times for one view class,
        # we only need to extract info from view class once since it will
        # loop all the methods of the class.
        if hasattr(view_func, '_method_spec'):
            return view_func
        view_func._method_spec = {}
        if not hasattr(view_func, '_spec'):
            view_func._spec = {}
        for method_name in view_class.methods:  # type: ignore
            # method_name: ['GET', 'POST', ...]
            method = view_class.__dict__[method_name.lower()]
            # collect spec info from class attribute "decorators"
            if hasattr(view_func, '_spec') and view_func._spec != {}:
                if not hasattr(method, '_spec'):
                    method._spec = view_func._spec
                else:
                    for key, value in view_func._spec.items():
                        if value is not None and method._spec.get(key) is None:
                            method._spec[key] = value
            else:
                if not hasattr(method, '_spec'):
                    method._spec = {'no_spec': True}
            if not method._spec.get('summary'):
                method._spec['summary'] = get_path_summary(
                    method, f'{method_name.title()} {view_class.__name__}'
                )
                method._spec['generated_summary'] = True
            if not method._spec.get('description'):
                method._spec['description'] = get_path_description(method)
                method._spec['generated_description'] = True
            view_func._method_spec[method_name] = method._spec
        return view_func

    def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = None,
        view_func: t.Optional[ViewFuncOrClassType] = None,
        **options: t.Any,
    ):
        """Record the spec for view classes before calling the actual `add_url_rule` method.

        When calling this method directly, the `view_func` argument can be a view function or
        a view function created by `ViewClass.as_view()`. It only accepts a view class when
        using the route decorator on a view class.
        """
        view_class: ViewClassType
        is_view_class: bool = False

        if hasattr(view_func, 'view_class'):
            # a function returned by MethodViewClass.as_view()
            is_view_class = True
            view_class = view_func.view_class  # type: ignore
        elif isinstance(view_func, type(MethodView)):
            # a MethodView class passed with the route decorator
            is_view_class = True
            view_class = view_func  # type: ignore
            if endpoint is None:
                endpoint = view_class.__name__
            view_func = view_class.as_view(endpoint)

        if is_view_class and hasattr(self, 'enable_openapi') and self.enable_openapi:
            view_func = record_spec_for_view_class(view_func, view_class)  # type: ignore

        super(cls, self).add_url_rule(rule, endpoint, view_func, **options)

    cls.add_url_rule = add_url_rule
    return cls
