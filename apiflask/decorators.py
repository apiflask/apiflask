from functools import wraps

from flask import Response, jsonify, current_app
from webargs.flaskparser import FlaskParser as BaseFlaskParser

from .exceptions import ValidationError


class FlaskParser(BaseFlaskParser):

    def handle_error(self, error, req, schema, *, error_status_code,
                     error_headers):
        raise ValidationError(
            error_status_code or current_app.config['VALIDATION_ERROR_CODE'],
            current_app.config['VALIDATION_ERROR_DESCRIPTION'],
            error.messages)


parser = FlaskParser()
use_args = parser.use_args


def _annotate(f, **kwargs):
    if not hasattr(f, '_spec'):
        f._spec = {}
    for key, value in kwargs.items():
        f._spec[key] = value


def auth_required(auth, **kwargs):
    def decorator(f):
        roles = kwargs.get('role')
        if not isinstance(roles, list):  # pragma: no cover
            roles = [roles] if roles is not None else []
        _annotate(f, auth=auth, roles=roles)
        return auth.login_required(**kwargs)(f)
    return decorator


def input(schema, location='json', **kwargs):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        if location == 'json':
            _annotate(f, body=schema)
        else:
            if not hasattr(f, '_spec') or f._spec.get('args') is None:
                _annotate(f, args=[])
            f._spec['args'].append((schema, location))
        return use_args(schema, location=location, **kwargs)(f)
    return decorator


def output(schema, status_code=200, description=None):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        _annotate(f, response=schema, status_code=status_code,
                  response_description=description)

        sentinel = object()

        def _jsonify(obj, many=sentinel, *args, **kwargs):
            """Copy from flask_marshmallow.schemas.Schema.jsonify"""
            if many is sentinel:
                many = schema.many
            data = schema.dump(obj, many=many)
            return jsonify(data, *args, **kwargs)

        @wraps(f)
        def _response(*args, **kwargs):
            rv = f(*args, **kwargs)
            if isinstance(rv, Response):  # pragma: no cover
                raise RuntimeError(
                    'The @output decorator cannot handle Response objects.')
            if isinstance(rv, tuple):
                json = _jsonify(rv[0])
                if len(rv) == 2:
                    if not isinstance(rv[1], int):
                        rv = (json, status_code, rv[1])
                    else:
                        rv = (json, rv[1])
                elif len(rv) >= 3:
                    rv = (json, rv[1], rv[2])
                else:
                    rv = (json, status_code)
                return rv
            else:
                return _jsonify(rv), status_code
        return _response
    return decorator


def doc(
    summary=None,
    description=None,
    tag=None,
    responses=None,
    deprecated=None,
    hide=False
):
    """
    Set up OpenAPI documentation for view function.

    :param summary: The summary of this view function. If not set, the name of
        the view function will be used. If your view function named with ``get_pet``,
        then the summary will be "Get Pet". If the view function has docstring, then
        the first line of the docstring will be used. The precedence will be:
        @doc(summary='blah') > the frist line of docstring > the view functino name
    :param description: The description of this view function. If not set, the lines
        after the empty line of the docstring will be used.
    :param tag: The tag of this view function, map the tag you passed in the :attr:`tags`
        attribute. If app.tags not set, the blueprint name will be used as tag name.
    :param responses: The other responses for this view function, accept a dict in a format
        of ``{400: 'Bad Request'}``.
    :param deprecated: Flag this endpoint as deprecated in API docs. Defaults to ``None``.
    :param hide: Hide this endpoint in API docs. Defaults to ``False``.

    .. versionadded:: 0.2.0
    """
    def decorator(f):
        _annotate(
            f,
            summary=summary,
            description=description,
            tag=tag,
            responses=responses,
            deprecated=deprecated,
            hide=hide
        )
        return f
    return decorator
