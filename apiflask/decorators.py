from typing import Callable, Union, List, Optional, Dict, Any, Type, Mapping
from functools import wraps

from flask import Response
from flask import jsonify
from flask import current_app
from webargs.flaskparser import FlaskParser as BaseFlaskParser
from marshmallow import ValidationError as MarshmallowValidationError

from .errors import ValidationError
from .utils import _sentinel
from .schemas import Schema
from .schemas import EmptySchema
from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .types import DecoratedType
from .types import ResponseType
from .types import RequestType


class FlaskParser(BaseFlaskParser):

    def handle_error(  # type: ignore
        self,
        error: MarshmallowValidationError,
        req: RequestType,
        schema: Schema,
        *,
        error_status_code: int,
        error_headers: Mapping[str, str]
    ) -> None:
        raise ValidationError(
            error_status_code or current_app.config['VALIDATION_ERROR_STATUS_CODE'],
            current_app.config['VALIDATION_ERROR_DESCRIPTION'],
            error.messages,
            error_headers
        )


parser: FlaskParser = FlaskParser()
use_args: Callable = parser.use_args


def _annotate(f: Any, **kwargs: Any) -> None:
    if not hasattr(f, '_spec'):
        f._spec = {}
    for key, value in kwargs.items():
        f._spec[key] = value


def auth_required(
    auth: Union[Type[HTTPBasicAuth], Type[HTTPTokenAuth]],
    role: Optional[Union[list, str]] = None,
    optional: Optional[str] = None
) -> Callable[[DecoratedType], DecoratedType]:
    roles = role
    if not isinstance(role, list):  # pragma: no cover
        roles = [role] if role is not None else []

    def decorator(f):
        _annotate(f, auth=auth, roles=roles)
        return auth.login_required(role=role, optional=optional)(f)
    return decorator


def input(
    schema: Schema,
    location: str = 'json',
    **kwargs: Any
) -> Callable[[DecoratedType], DecoratedType]:
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        if location not in [
            'json', 'query', 'headers', 'cookies', 'files', 'form', 'querystring'
        ]:
            raise RuntimeError(
                f'''
                Unknown input location. The supported locations are: 'json', 'files',
                'form', 'cookies', 'headers', 'query' (same as 'querystring'). Got
                '{location}' instead.
                '''
            )
        if location == 'json':
            _annotate(f, body=schema)
        else:
            if not hasattr(f, '_spec') or f._spec.get('args') is None:
                _annotate(f, args=[])
            f._spec['args'].append((schema, location))
        return use_args(schema, location=location, **kwargs)(f)
    return decorator


def output(
    schema: Schema,
    status_code: int = 200,
    description: Optional[str] = None
) -> Callable[[DecoratedType], DecoratedType]:
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    if isinstance(schema, EmptySchema):
        status_code = 204

    def decorator(f):
        _annotate(f, response={
            'schema': schema,
            'status_code': status_code,
            'description': description
        })

        def _jsonify(obj, many=_sentinel, *args, **kwargs):  # pragma: no cover
            """From Flask-Marshmallow, see NOTICE file for license informaiton."""
            if many is _sentinel:
                many = schema.many
            data = schema.dump(obj, many=many)
            return jsonify(data, *args, **kwargs)

        @wraps(f)
        def _response(*args: Any, **kwargs: Any) -> ResponseType:
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
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tag: Optional[Union[List[str], List[Dict[str, Any]]]] = None,
    responses: Optional[Union[List[int], Dict[int, str]]] = None,
    deprecated: Optional[bool] = False,
    hide: Optional[bool] = False
) -> Callable[[DecoratedType], DecoratedType]:
    """
    Set up OpenAPI documentation for view function.

    Arguments:
        summary: The summary of this view function. If not set, the name of
            the view function will be used. If your view function named with `get_pet`,
            then the summary will be "Get Pet". If the view function has docstring, then
            the first line of the docstring will be used. The precedence will be:
            @doc(summary='blah') > the frist line of docstring > the view functino name
        description: The description of this view function. If not set, the lines
            after the empty line of the docstring will be used.
        tag: The tag list of this view function, map the tags you passed in the :attr:`tags`
            attribute. You can pass a list of tag names or just a single tag string. If `app.tags`
            not set, the blueprint name will be used as tag name.
        responses: The other responses for this view function, accept a dict in a format
            of `{400: 'Bad Request'}`.
        deprecated: Flag this endpoint as deprecated in API docs. Defaults to `False`.
        hide: Hide this endpoint in API docs. Defaults to `False`.

    .. versionchanged:: 0.3.0
    - Change the default value of `deprecated` from `None` to `False`.
    - Rename `tags` to `tag`.

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
