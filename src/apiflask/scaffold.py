import typing as t
import warnings
from collections.abc import Mapping as ABCMapping
from functools import wraps

import flask
from flask import current_app
from flask import jsonify
from flask import Response
from flask.views import MethodView
from marshmallow import ValidationError as MarshmallowValidationError
from webargs.flaskparser import FlaskParser as BaseFlaskParser
from webargs.multidictproxy import MultiDictProxy

from .exceptions import _ValidationError
from .helpers import _sentinel
from .schemas import EmptySchema
from .schemas import Schema
from .types import DecoratedType
from .types import DictSchemaType
from .types import HTTPAuthType
from .types import OpenAPISchemaType
from .types import RequestType
from .types import ResponseReturnValueType
from .types import SchemaType

BODY_LOCATIONS = ['json', 'files', 'form', 'form_and_files', 'json_or_form']
SUPPORTED_LOCATIONS = BODY_LOCATIONS + [
    'query', 'headers', 'cookies', 'querystring', 'path', 'view_args'
]


class FlaskParser(BaseFlaskParser):
    """Overwrite the default `webargs.FlaskParser.handle_error`.

    Update the default status code and the error description from related
    configuration variables.
    """

    def handle_error(  # type: ignore
        self,
        error: MarshmallowValidationError,
        req: RequestType,
        schema: Schema,
        *,
        error_status_code: int,
        error_headers: t.Mapping[str, str]
    ) -> None:
        raise _ValidationError(
            error_status_code or current_app.config['VALIDATION_ERROR_STATUS_CODE'],
            current_app.config['VALIDATION_ERROR_DESCRIPTION'],
            error.messages,
            error_headers
        )


parser: FlaskParser = FlaskParser()
use_args: t.Callable = parser.use_args


def _get_files_and_form(request, schema):
    form_and_files_data = request.files.copy()
    form_and_files_data.update(request.form)
    return MultiDictProxy(form_and_files_data, schema)


@parser.location_loader('form_and_files')
def load_form_and_files(request, schema):
    return _get_files_and_form(request, schema)


@parser.location_loader('files')
def load_files(request, schema):
    return _get_files_and_form(request, schema)


def _annotate(f: t.Any, **kwargs: t.Any) -> None:
    if not hasattr(f, '_spec'):
        f._spec = {}
    for key, value in kwargs.items():
        f._spec[key] = value


def _ensure_sync(f):
    if flask.__version__ < '2.' or hasattr(f, '_sync_ensured'):
        return f

    @wraps(f)
    def wrapper(*args, **kwargs):
        return current_app.ensure_sync(f)(*args, **kwargs)

    wrapper._sync_ensured = True
    return wrapper


def _generate_schema_from_mapping(
    schema: DictSchemaType,
    schema_name: t.Optional[str]
) -> t.Type[Schema]:
    if schema_name is None:
        schema_name = 'GeneratedSchema'
    return Schema.from_dict(schema, name=schema_name)()  # type: ignore


class APIScaffold:
    """A base class for [`APIFlask`][apiflask.app.APIFlask] and
    [`APIBlueprint`][apiflask.blueprint.APIBlueprint].

    This class contains the route shortcut decorators (i.e. `get`, `post`, etc.) and
    API-related decorators (i.e. `auth_required`, `input`, `output`, `doc`).

    *Version added: 1.0*
    """
    def _method_route(self, method: str, rule: str, options: t.Any):
        if 'methods' in options:
            raise RuntimeError('Use the "route" decorator to use the "methods" argument.')

        def decorator(f):
            if isinstance(f, type(MethodView)):
                raise RuntimeError(
                    'The route shortcuts cannot be used with "MethodView" classes, '
                    'use the "route" decorator instead.'
                )
            return self.route(rule, methods=[method], **options)(f)
        return decorator

    def get(self, rule: str, **options: t.Any):
        """Shortcut for `app.route()` or `app.route(methods=['GET'])`."""
        return self._method_route('GET', rule, options)

    def post(self, rule: str, **options: t.Any):
        """Shortcut for `app.route(methods=['POST'])`."""
        return self._method_route('POST', rule, options)

    def put(self, rule: str, **options: t.Any):
        """Shortcut for `app.route(methods=['PUT'])`."""
        return self._method_route('PUT', rule, options)

    def patch(self, rule: str, **options: t.Any):
        """Shortcut for `app.route(methods=['PATCH'])`."""
        return self._method_route('PATCH', rule, options)

    def delete(self, rule: str, **options: t.Any):
        """Shortcut for `app.route(methods=['DELETE'])`."""
        return self._method_route('DELETE', rule, options)

    def auth_required(
        self,
        auth: HTTPAuthType,
        role: t.Optional[str] = None,
        roles: t.Optional[list] = None,
        optional: t.Optional[str] = None
    ) -> t.Callable[[DecoratedType], DecoratedType]:
        """Protect a view with provided authentication settings.

        > Be sure to put it under the routes decorators (i.e., `app.route`, `app.get`,
        `app.post`, etc.).

        Examples:

        ```python
        from apiflask import APIFlask, HTTPTokenAuth

        app = APIFlask(__name__)
        auth = HTTPTokenAuth()

        @app.get('/')
        @app.auth_required(auth)
        def hello():
            return 'Hello'!
        ```

        Arguments:
            auth: The `auth` object, an instance of
                [`HTTPBasicAuth`][apiflask.security.HTTPBasicAuth]
                or [`HTTPTokenAuth`][apiflask.security.HTTPTokenAuth].
            role: Deprecated since 1.0, use `roles` instead.
            roles: The selected roles to allow to visit this view, accepts a list of role names.
                See [Flask-HTTPAuth's documentation][_role]{target:_blank} for more details.
                [_role]: https://flask-httpauth.readthedocs.io/en/latest/#user-roles
            optional: Set to `True` to allow the view to execute even the authentication
                information is not included with the request, in which case the attribute
                `auth.current_user` will be `None`.

        *Version changed: 1.0.0*

        - The `role` parameter is deprecated.

        *Version changed: 0.12.0*

        - Move to `APIFlask` and `APIBlueprint` classes.

        *Version changed: 0.4.0*

        - Add parameter `roles`.
        """
        _roles = None
        if role is not None:
            warnings.warn(
                'The `role` parameter is deprecated and will be removed in 1.1, '
                'use `roles` and always pass a list instead.',
                DeprecationWarning,
                stacklevel=3,
            )
            _roles = [role]
        elif roles is not None:
            _roles = roles

        def decorator(f):
            f = _ensure_sync(f)
            _annotate(f, auth=auth, roles=_roles or [])
            return auth.login_required(role=_roles, optional=optional)(f)
        return decorator

    def input(
        self,
        schema: SchemaType,
        location: str = 'json',
        schema_name: t.Optional[str] = None,
        example: t.Optional[t.Any] = None,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        **kwargs: t.Any
    ) -> t.Callable[[DecoratedType], DecoratedType]:
        """Add input settings for view functions.

        > Be sure to put it under the routes decorators (i.e., `app.route`, `app.get`,
        `app.post`, etc.).

        If the validation passed, the data will inject into view
        function as a positional argument in the form of `dict`. Otherwise,
        an error response with the detail of the validation result will be returned.

        Examples:

        ```python
        from apiflask import APIFlask

        app = APIFlask(__name__)

        @app.get('/')
        @app.input(PetInSchema)
        def hello(parsed_and_validated_input_data):
            print(parsed_and_validated_input_data)
            return 'Hello'!
        ```

        Arguments:
            schema: The marshmallow schema of the input data.
            location: The location of the input data, one of `'json'` (default),
                `'files'`, `'form'`, `'cookies'`, `'headers'`, `'query'`
                (same as `'querystring'`).
            schema_name: The schema name for dict schema, only needed when you pass
                a schema dict (e.g., `{'name': String(required=True)}`) for `json`
                location.
            example: The example data in dict for request body, you should use either
                `example` or `examples`, not both.
            examples: Multiple examples for request body, you should pass a dict
                that contains multiple examples. Example:

                ```python
                {
                    'example foo': {  # example name
                        'summary': 'an example of foo',  # summary field is optional
                        'value': {'name': 'foo', 'id': 1}  # example value
                    },
                    'example bar': {
                        'summary': 'an example of bar',
                        'value': {'name': 'bar', 'id': 2}
                    },
                }
                ```

        *Version changed: 1.0*

        - Ensure only one input body location was used.
        - Add `form_and_files` and `json_or_form` (from webargs) location.
        - Rewrite `files` to act as `form_and_files`.
        - Use correct request content type for `form` and `files`.

        *Version changed: 0.12.0*

        - Move to APIFlask and APIBlueprint classes.

        *Version changed: 0.4.0*

        - Add parameter `examples`.
        """
        if isinstance(schema, ABCMapping):
            schema = _generate_schema_from_mapping(schema, schema_name)
        if isinstance(schema, type):  # pragma: no cover
            schema = schema()

        def decorator(f):
            f = _ensure_sync(f)
            is_body_location = location in BODY_LOCATIONS
            if is_body_location and hasattr(f, '_spec') and 'body' in f._spec:
                raise RuntimeError(
                    'When using the app.input() decorator, you can only declare one request '
                    'body location (one of "json", "form", "files", "form_and_files", '
                    'and "json_or_form").'
                )
            if location not in SUPPORTED_LOCATIONS:
                raise ValueError(
                    'Unknown input location. The supported locations are: "json", "files",'
                    ' "form", "cookies", "headers", "query" (same as "querystring"), "path"'
                    f' (same as "view_args") and "form_and_files". Got "{location}" instead.'
                )
            if location == 'json':
                _annotate(f, body=schema, body_example=example, body_examples=examples)
            elif location == 'form':
                _annotate(
                    f,
                    body=schema,
                    body_example=example,
                    body_examples=examples,
                    content_type='application/x-www-form-urlencoded'
                )
            elif location in ['files', 'form_and_files']:
                _annotate(
                    f,
                    body=schema,
                    body_example=example,
                    body_examples=examples,
                    content_type='multipart/form-data'
                )
            else:
                if not hasattr(f, '_spec') or f._spec.get('args') is None:
                    _annotate(f, args=[])
                # TODO: Support set example for request parameters
                f._spec['args'].append((schema, location))
            return use_args(schema, location=location, **kwargs)(f)
        return decorator

    def output(
        self,
        schema: SchemaType,
        status_code: int = 200,
        description: t.Optional[str] = None,
        schema_name: t.Optional[str] = None,
        example: t.Optional[t.Any] = None,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        links: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> t.Callable[[DecoratedType], DecoratedType]:
        """Add output settings for view functions.

        > Be sure to put it under the routes decorators (i.e., `app.route`, `app.get`,
        `app.post`, etc.).

        The decorator will format the return value of your view function with
        provided marshmallow schema. You can return a dict or an object (such
        as a model class instance of ORMs). APIFlask will handle the formatting
        and turn your return value into a JSON response.

        P.S. The output data will not be validated; it's a design choice of marshmallow.
        marshmallow 4.0 may be support the output validation.

        Examples:

        ```python
        from apiflask import APIFlask

        app = APIFlask(__name__)

        @app.get('/')
        @app.output(PetOutSchema)
        def hello():
            return the_dict_or_object_match_petout_schema
        ```

        Arguments:
            schema: The schemas of the output data.
            status_code: The status code of the response, defaults to `200`.
            description: The description of the response.
            schema_name: The schema name for dict schema, only needed when you pass
                a schema dict (e.g., `{'name': String()}`).
            example: The example data in dict for response body, you should use either
                `example` or `examples`, not both.
            examples: Multiple examples for response body, you should pass a dict
                that contains multiple examples. Example:

                ```python
                {
                    'example foo': {  # example name
                        'summary': 'an example of foo',  # summary field is optional
                        'value': {'name': 'foo', 'id': 1}  # example value
                    },
                    'example bar': {
                        'summary': 'an example of bar',
                        'value': {'name': 'bar', 'id': 2}
                    },
                }
                ```
            links: The `links` of response. It accepts a dict which maps a link name to
                a link object. Example:

                ```python
                {
                    'getAddressByUserId': {
                        'operationId': 'getUserAddress',
                        'parameters': {
                            'userId': '$request.path.id'
                        }
                    }
                }
                ```

                See the [docs](https://apiflask.com/openapi/#response-links) for more details
                about setting response links.

        *Version changed: 0.12.0*

        - Move to APIFlask and APIBlueprint classes.

        *Version changed: 0.10.0*

        - Add `links` parameter.

        *Version changed: 0.9.0*

        - Add base response customization support.

        *Version changed: 0.6.0*

        - Support decorating async views.

        *Version changed: 0.5.2*

        - Return the `Response` object directly.

        *Version changed: 0.4.0*

        - Add parameter `examples`.
        """
        if schema == {}:
            schema = EmptySchema
        if isinstance(schema, ABCMapping):
            schema = _generate_schema_from_mapping(schema, schema_name)
        if isinstance(schema, type):  # pragma: no cover
            schema = schema()

        if isinstance(schema, EmptySchema):
            status_code = 204

        def decorator(f):
            f = _ensure_sync(f)
            _annotate(f, response={
                'schema': schema,
                'status_code': status_code,
                'description': description,
                'example': example,
                'examples': examples,
                'links': links,
            })

            def _jsonify(
                obj: t.Any,
                many: bool = _sentinel,  # type: ignore
                *args: t.Any,
                **kwargs: t.Any
            ) -> Response:  # pragma: no cover
                """From Flask-Marshmallow, see the NOTICE file for license information."""
                if many is _sentinel:
                    many = schema.many  # type: ignore
                base_schema: OpenAPISchemaType = current_app.config['BASE_RESPONSE_SCHEMA']
                if base_schema is not None and status_code != 204:
                    data_key: str = current_app.config['BASE_RESPONSE_DATA_KEY']
                    if data_key not in obj:
                        raise RuntimeError(
                            f'The data key "{data_key}" is not found in the returned dict.'
                        )
                    obj[data_key] = schema.dump(obj[data_key], many=many)  # type: ignore
                    data = base_schema().dump(obj)  # type: ignore
                else:
                    data = schema.dump(obj, many=many)  # type: ignore
                return jsonify(data, *args, **kwargs)

            @wraps(f)
            def _response(*args: t.Any, **kwargs: t.Any) -> ResponseReturnValueType:
                rv = f(*args, **kwargs)
                if isinstance(rv, Response):
                    return rv
                if not isinstance(rv, tuple):
                    return _jsonify(rv), status_code
                json = _jsonify(rv[0])
                if len(rv) == 2:
                    rv = (json, rv[1]) if isinstance(rv[1], int) else (json, status_code, rv[1])
                elif len(rv) >= 3:
                    rv = (json, rv[1], rv[2])
                else:
                    rv = (json, status_code)
                return rv  # type: ignore
            return _response
        return decorator

    def doc(
        self,
        summary: t.Optional[str] = None,
        description: t.Optional[str] = None,
        tag: t.Optional[str] = None,
        tags: t.Optional[t.List[str]] = None,
        responses: t.Optional[t.Union[t.List[int], t.Dict[int, str]]] = None,
        deprecated: t.Optional[bool] = None,
        hide: t.Optional[bool] = None,
        operation_id: t.Optional[str] = None,
        security: t.Optional[t.Union[str, t.List[t.Union[str, t.Dict[str, list]]]]] = None,
    ) -> t.Callable[[DecoratedType], DecoratedType]:
        """Set up the OpenAPI Spec for view functions.

        > Be sure to put it under the routes decorators (i.e., `app.route`, `app.get`,
        `app.post`, etc.).

        Examples:

        ```python
        from apiflask import APIFlask

        app = APIFlask(__name__)

        @app.get('/')
        @app.doc(summary='Say hello', tags=['Foo'])
        def hello():
            return 'Hello'
        ```

        Arguments:
            summary: The summary of this endpoint. If not set, the name of the view function
                will be used. If your view function is named with `get_pet`, then the summary
                will be "Get Pet". If the view function has a docstring, then the first
                line of the docstring will be used. The precedence will be:

                ```
                @app.doc(summary='blah') > the first line of docstring > the view function name
                ```

            description: The description of this endpoint. If not set, the lines after the empty
                line of the docstring will be used.
            tag: Deprecated since 1.0, use `tags` instead.
            tags: A list of tag names of this endpoint, map the tags you passed in the `app.tags`
                attribute. If `app.tags` is not set, the blueprint name will be used as tag name.
            responses: The other responses for this view function, accepts a dict in a format
                of `{404: 'Not Found'}` or a list of status code (`[404, 418]`). If pass a dict,
                and a response with the same status code is already exist, the existing
                description will be overwritten.
            deprecated: Flag this endpoint as deprecated in API docs.
            hide: Hide this endpoint in API docs.
            operation_id: The `operationId` of this endpoint. Set config `AUTO_OPERATION_ID` to
                `True` to enable the auto-generating of operationId (in the format of
                `{method}_{endpoint}`).
            security: The `security` used for this endpoint. Match the security info specified in
                the `SECURITY_SCHEMES` configuration. If you don't need specify the scopes, just
                pass a security name (equals to `[{'foo': []}]`) or a list of security names (equals
                to `[{'foo': []}, {'bar': []}]`).

        *Version changed: 1.0*

        - Add `security` parameter to support customizing security info.
        - The `role` parameter is deprecated.

        *Version changed: 0.12.0*

        - Move to `APIFlask` and `APIBlueprint` classes.

        *Version changed: 0.10.0*

        - Add parameter `operation_id`.

        *Version changed: 0.5.0*

        - Change the default value of parameters `hide` and `deprecated` from `False` to `None`.

        *Version changed: 0.4.0*

        - Add parameter `tag`.

        *Version changed: 0.3.0*

        - Change the default value of `deprecated` from `None` to `False`.
        - Rename parameter `tags` to `tag`.

        *Version added: 0.2.0*
        """
        _tags = None
        if tag is not None:
            warnings.warn(
                'The `tag` parameter is deprecated and will be removed in 1.1, '
                'use `tags` and always pass a list instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            _tags = [tag]
        elif tags is not None:
            _tags = tags

        def decorator(f):
            f = _ensure_sync(f)
            _annotate(
                f,
                summary=summary,
                description=description,
                tags=_tags,
                responses=responses,
                deprecated=deprecated,
                hide=hide,
                operation_id=operation_id,
                security=security,
            )
            return f
        return decorator
