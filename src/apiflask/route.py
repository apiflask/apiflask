import typing as t

from flask.views import MethodView as FlaskMethodView
from flask.views import View as FlaskView

from .openapi import get_path_description
from .openapi import get_path_summary
from .types import ViewClassType
from .types import ViewFuncOrClassType
from .types import ViewFuncType
from .views import MethodView


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
        if not view_class.methods:  # no methods defined
            return view_func
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
        provide_automatic_options: t.Optional[bool] = None,
        **options: t.Any,
    ):
        """Record the spec for view classes before calling the actual `add_url_rule` method.

        When calling this method directly, the `view_func` argument can be a view function or
        a view function created by `ViewClass.as_view()`. It only accepts a view class when
        using the route decorator on a view class.
        """
        if isinstance(view_func, type):
            # call as_view() for MethodView passed with @route
            if endpoint is None:
                endpoint = view_func.__name__
            view_func = view_func.as_view(endpoint)  # type: ignore

        if hasattr(view_func, 'view_class'):
            # view function created with MethodViewClass.as_view()
            view_class = view_func.view_class  # type: ignore
            if not issubclass(view_class, MethodView):
                # skip View-based class
                view_func._spec = {'hide': True}  # type: ignore
            else:
                # record spec for MethodView class
                if hasattr(self, 'enable_openapi') and self.enable_openapi:
                    view_func = record_spec_for_view_class(view_func, view_class)  # type: ignore

            # view func created by Flask's View only accpets keyword arguments
            if issubclass(view_class, FlaskView):
                view_func._only_kwargs = True  # type: ignore

            if issubclass(view_class, FlaskMethodView):
                raise RuntimeError(
                    'APIFlask only supports generating OpenAPI spec for view classes created '
                    'with apiflask.views.MethodView (`from apiflask.views import MethodView`).',
                )

        super(cls, self).add_url_rule(
            rule,
            endpoint,
            view_func,
            provide_automatic_options=provide_automatic_options,
            **options
        )

    cls.add_url_rule = add_url_rule
    return cls
