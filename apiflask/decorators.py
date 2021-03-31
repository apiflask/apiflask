from typing import Callable, Union, List, Optional, Dict, Any, Type, Mapping
from functools import wraps
from collections.abc import Mapping as ABCMapping

from flask import Response
from flask import jsonify
from flask import current_app
from webargs.flaskparser import FlaskParser as BaseFlaskParser
from marshmallow import ValidationError as MarshmallowValidationError

from .exceptions import ValidationError
from .utils import _sentinel
from .schemas import Schema
from .schemas import EmptySchema
from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .types import DecoratedType
from .types import ResponseType
from .types import RequestType


class FlaskParser(BaseFlaskParser):
    """Overwrite the default `webargs.FlaskParser.handle_error` to
    change the default status code and the error description.
    """

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
    """Protect a view with provided authentication settings.

    > Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

    Examples:

    ```python
    from apiflask import APIFlask, HTTPTokenAuth, auth_required

    app = APIFlask(__name__)
    auth = HTTPTokenAuth()

    @app.get('/')
    @auth_required(auth)
    def hello():
        return 'Hello'!
    ```

    Arguments:
        auth: The `auth` object, an instance of [`HTTPBasicAuth`][apiflask.security.HTTPBasicAuth]
            or [`HTTPTokenAuth`][apiflask.security.HTTPTokenAuth].
        role: The selected role to allow to visit this view, accepts a string or a list.
            See [Flask-HTTPAuth's documentation](role) for more details.
        optional: To allow the view to execute even the authentication information
            is not included with the request, in which case `auth.current_user` will be `None`.

    [role]: https://flask-httpauth.readthedocs.io/en/latest/#user-roles
    """
    roles = role
    if not isinstance(role, list):  # pragma: no cover
        roles = [role] if role is not None else []

    def decorator(f):
        _annotate(f, auth=auth, roles=roles)
        return auth.login_required(role=role, optional=optional)(f)
    return decorator


def _generate_schema_from_mapping(schema, schema_name):
    if schema_name is None:
        schema_name = 'GeneratedSchema'
    return Schema.from_dict(schema, name=schema_name)()


def input(
    schema: Schema,
    location: str = 'json',
    schema_name: Optional[str] = None,
    example: Optional[Any] = None,
    **kwargs: Any
) -> Callable[[DecoratedType], DecoratedType]:
    """Add input settings for view functions.

    > Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

    If the validation passed, the data will be inject to view
    function as a positional argument in the form of `dict`. Otherwise,
    an error response with the detail of validation result will be returned.

    Examples:

    ```python
    from apiflask import APIFlask, input

    app = APIFlask(__name__)

    @app.get('/')
    @input(PetInSchema)
    def hello(parsed_and_validated_input_data):
        print(parsed_and_validated_input_data)
        return 'Hello'!
    ```

    Arguments:
        schema: The Marshmallow schema used to validate the input data.
        location: The location of the input data, one of `'json'` (default),
            `'files'`, `'form'`, `'cookies'`, `'headers'`, `'query'`
            (same as `'querystring'`).
        schema_name: The schema name for dict schema, only needed when you pass
            a `dict` schema (e.g. `{'name': String(required=True)}`) for `json`
            location.
        example: The example data for request body.
    """
    if isinstance(schema, ABCMapping):
        schema = _generate_schema_from_mapping(schema, schema_name)
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        if location not in [
            'json', 'query', 'headers', 'cookies', 'files', 'form', 'querystring'
        ]:
            raise RuntimeError(
                'Unknown input location. The supported locations are: "json", "files",'
                ' "form", "cookies", "headers", "query" (same as "querystring").'
                f' Got "{location}" instead.'
            )
        if location == 'json':
            _annotate(f, body=schema, body_example=example)
        else:
            if not hasattr(f, '_spec') or f._spec.get('args') is None:
                _annotate(f, args=[])
            # Todo: Support set example for request parameters
            f._spec['args'].append((schema, location))
        return use_args(schema, location=location, **kwargs)(f)
    return decorator


def output(
    schema: Schema,
    status_code: int = 200,
    description: Optional[str] = None,
    schema_name: Optional[str] = None,
    example: Optional[Any] = None
) -> Callable[[DecoratedType], DecoratedType]:
    """Add output settings for view functions.

    > Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

    The decorator will formatting the return value of your view
    function with provided Marshmallow schema. You can just return a
    dict or an object (such as a Model instance of ORMs). APIFlask will
    handle the formatting and turn your return value into a JSON response.

    P.S. The output data will not be validated, it's a design choice of Marshmallow.
    This output validation may be supported in Marshmallow 4.0.

    Examples:

    ```python
    from apiflask import APIFlask, output

    app = APIFlask(__name__)

    @app.get('/')
    @output(PetOutSchema)
    def hello():
        return the_dict_or_object_match_petout_schema
    ```

    Arguments:
        schema: The schemas of the output data.
        status_code: The status code of the response, defaults to `200`.
        description: The description of the response.
        schema_name: The schema name for dict schema, only needed when you pass
            a `dict` schema (e.g. `{'name': String()}`).
        example: The example data for response.
    """
    if isinstance(schema, ABCMapping) and schema != {}:
        schema = _generate_schema_from_mapping(schema, schema_name)
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    if isinstance(schema, EmptySchema):
        status_code = 204

    def decorator(f):
        _annotate(f, response={
            'schema': schema,
            'status_code': status_code,
            'description': description,
            'example': example
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
    """Set up the OpenAPI Spec for view functions.

    > Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

    Examples:

    ```python
    from apiflask import APIFlask, doc

    app = APIFlask(__name__)

    @app.get('/')
    @doc(summary='Say hello', tag='Foo')
    def hello():
        return 'Hello'!
    ```

    Arguments:
        summary: The summary of this endpoint. If not set, the name of the view function
            will be used. If your view function named with `get_pet`, then the summary
            will be "Get Pet". If the view function has docstring, then the first line of
            the docstring will be used. The precedence will be:
            ```
            @doc(summary='blah') > the first line of docstring > the view function name
            ```
        description: The description of this endpoint. If not set, the lines after the empty
            line of the docstring will be used.
        tag: The tag or tag list of this endpoint, map the tags you passed in the `app.tags`
            attribute. You can pass a list of tag names or just a single tag name string.
            If `app.tags` not set, the blueprint name will be used as tag name.
        responses: The other responses for this view function, accept a dict in a format
            of `{404: 'Not Found'}` or a list of status_code (`[404, 418]`).
        deprecated: Flag this endpoint as deprecated in API docs. Defaults to `False`.
        hide: Hide this endpoint in API docs. Defaults to `False`.

    *Version changed: 0.3.0*

    - Change the default value of `deprecated` from `None` to `False`.
    - Rename argument `tags` to `tag`.

    *Version added: 0.2.0*
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
