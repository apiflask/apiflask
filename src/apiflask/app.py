import json
import re
import sys
import typing as t
import warnings

# temp fix for https://github.com/django/asgiref/issues/143
if sys.platform == 'win32' and (3, 8, 0) <= sys.version_info < (3, 9, 0):  # pragma: no cover
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # pragma: no cover

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import render_template_string
from flask.config import ConfigAttribute
from flask.globals import _request_ctx_stack

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from flask_marshmallow import fields
    try:
        from flask_marshmallow import sqla
    except ImportError:
        sqla = None

from werkzeug.exceptions import HTTPException as WerkzeugHTTPException

from .exceptions import HTTPError
from .exceptions import _bad_schema_message
from .helpers import get_reason_phrase
from .route import route_shortcuts
from .route import route_patch
from .schemas import Schema
from .types import ResponseType
from .types import ViewFuncType
from .types import ErrorCallbackType
from .types import SpecCallbackType
from .types import SchemaType
from .types import HTTPAuthType
from .types import TagsType
from .types import OpenAPISchemaType
from .openapi import add_response
from .openapi import add_response_with_schema
from .openapi import default_response
from .openapi import get_tag
from .openapi import get_operation_tags
from .openapi import get_path_summary
from .openapi import get_auth_name
from .openapi import get_argument
from .openapi import get_security_and_security_schemes
from .ui_templates import redoc_template
from .ui_templates import swagger_ui_template
from .ui_templates import swagger_ui_oauth2_redirect_template


@route_patch
@route_shortcuts
class APIFlask(Flask):
    """The `Flask` object with some web API support.

    Examples:

    ```python
    from apiflask import APIFlask

    app = APIFlask(__name__)
    ```

    Attributes:
        openapi_version: The version of OpenAPI Specification (openapi.openapi).
            This attribute can also be configured from the config with the
            `OPENAPI_VERSION` configuration key. Defaults to `'3.0.3'`.
        servers: The servers information of the API (openapi.servers), accepts
            multiple server dicts. Example value:

            ```python
            app.servers = [
                {
                    'name': 'Production Server',
                    'url': 'http://api.example.com'
                }
            ]
            ```

            This attribute can also be configured from the config with the
            `SERVERS` configuration key. Defaults to `None`.
        tags: The list of tags of the OpenAPI spec documentation (openapi.tags),
            accepts a list of dicts. You can also pass a simple list contains the
            tag name:

            ```python
            app.tags = ['foo', 'bar', 'baz']
            ```

            A standard OpenAPI tags list will look like this:

            ```python
            app.tags = [
                {'name': 'foo', 'description': 'The description of foo'},
                {'name': 'bar', 'description': 'The description of bar'},
                {'name': 'baz', 'description': 'The description of baz'}
            ]
            ```

            If not set, the blueprint names will be used as tags.

            This attribute can also be configured from the config with the
            `TAGS` configuration key. Defaults to `None`.
        external_docs: The external documentation information of the API
            (openapi.externalDocs). Example:

            ```python
            app.external_docs = {
                'description': 'Find more info here',
                'url': 'http://docs.example.com'
            }
            ```

            This attribute can also be configured from the config with the
            `EXTERNAL_DOCS` configuration key. Defaults to `None`.
        info: The info object (openapi.info), it accepts a dict contains following info fields:
            `description`, `termsOfService`, `contact`, `license`. You can use separate
            configuration variables to overwrite this dict. Example:

            ```python
            app.info = {
                'description': '...',
                'termsOfService': 'http://example.com',
                'contact': {
                    'name': 'API Support',
                    'url': 'http://www.example.com/support',
                    'email': 'support@example.com'
                },
                'license': {
                    'name': 'Apache 2.0',
                    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
                }
            }
            ```

        description: The description of the API (openapi.info.description).
            This attribute can also be configured from the config with the
            `DESCRIPTION` configuration key. Defaults to `None`.
        contact: The contact information of the API (openapi.info.contact). Example:

            ```python
            app.contact = {
                'name': 'API Support',
                'url': 'http://www.example.com/support',
                'email': 'support@example.com'
            }
            ```

            This attribute can also be configured from the config with the
            `CONTACT` configuration key. Defaults to `None`.
        license: The license of the API (openapi.info.license). Example:

            ```python
            app.license = {
                'name': 'Apache 2.0',
                'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
            }
            ```

            This attribute can also be configured from the config with the
            `LICENSE` configuration key. Defaults to `None`.
        terms_of_service: The terms of service URL of the API
            (openapi.info.termsOfService). Example:

            ```python
            app.terms_of_service = 'http://example.com/terms/'
            ```

            This attribute can also be configured from the config with the
            `TERMS_OF_SERVICE` configuration key. Defaults to `None`.
        spec_callback: It stores the function object registerd by
            [`spec_processor`][apiflask.APIFlask.spec_processor]. You can also
            pass a callback function to it directly without using `spec_processor`.
            Example:

            ```python
            def update_spec(spec):
                spec['title'] = 'Updated Title'
                return spec

            app.spec_callback = update_spec
            ```

        error_callback: It stores the function object registerd by
            [`error_processor`][apiflask.APIFlask.error_processor]. You can also
            pass a callback function to it directly without using `error_processor`.
            See the docstring of `error_processor` for more details.
            Example:

            ```python
            def my_error_handler(error):
                return {
                    'status_code': error.status_code,
                    'message': error.message,
                    'detail': error.detail
                }, error.status_code, error.headers

            app.error_processor = my_error_handler
            ```

        schema_name_resolver: It stores the function that used to decided the schema name.
            The schema name resolver should accept the schema object as argument and return
            the name.
            Example:

            ```python
            # this is the default schema name resolver used in APIFlask
            def schema_name_resolver(schema):
                name = schema.__class__.__name__  # get schema class name
                if name.endswith('Schema'):  # remove the "Schema" suffix
                    name = name[:-6] or name
                if schema.partial:  # add a "Update" suffix for partial schema
                    name += 'Update'
                return name

            app.schema_name_resolver = schema_name_resolver
            ```

    *Version changed: 0.9.0*

    - Add instance attribute `schema_name_resolver`.
    """

    openapi_version: str = ConfigAttribute('OPENAPI_VERSION')  # type: ignore
    tags: t.Optional[TagsType] = ConfigAttribute('TAGS')  # type: ignore
    servers: t.Optional[t.List[t.Dict[str, str]]] = ConfigAttribute('SERVERS')  # type: ignore
    info: t.Optional[t.Dict[str, t.Union[str, dict]]] = ConfigAttribute('INFO')  # type: ignore
    description: t.Optional[str] = ConfigAttribute('DESCRIPTION')  # type: ignore
    contact: t.Optional[t.Dict[str, str]] = ConfigAttribute('CONTACT')  # type: ignore
    license: t.Optional[t.Dict[str, str]] = ConfigAttribute('LICENSE')  # type: ignore
    external_docs: t.Optional[t.Dict[str, str]] = ConfigAttribute('EXTERNAL_DOCS')  # type: ignore
    terms_of_service: t.Optional[str] = ConfigAttribute('TERMS_OF_SERVICE')  # type: ignore

    def __init__(
        self,
        import_name: str,
        title: str = 'APIFlask',
        version: str = '0.1.0',
        spec_path: str = '/openapi.json',
        docs_path: str = '/docs',
        docs_oauth2_redirect_path: str = '/docs/oauth2-redirect',
        redoc_path: str = '/redoc',
        openapi_blueprint_url_prefix: t.Optional[str] = None,
        json_errors: bool = True,
        enable_openapi: bool = True,
        static_url_path: t.Optional[str] = None,
        static_folder: str = 'static',
        static_host: t.Optional[str] = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str = 'templates',
        instance_path: t.Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: t.Optional[str] = None
    ) -> None:
        """Make an app instance.

        Arguments:
            import_name: The name of the application package, usually
                `__name__`. This helps locate the `root_path` for the
                application.
            title: The title of the API (openapi.info.title), defaults to "APIFlask".
                You can change it to the name of your API (e.g., "Pet API").
            version: The version of the API (openapi.info.version), defaults to "0.1.0".
            spec_path: The path to OpenAPI Spec documentation. It
                defaults to `/openapi.json`, if the path ends with `.yaml`
                or `.yml`, the YAML format of the OAS will be returned.
            docs_path: The path to Swagger UI documentation, defaults to `/docs`.
            docs_oauth2_redirect_path: The path to Swagger UI OAuth redirect.
            redoc_path: The path to Redoc documentation, defaults to `/redoc`.
            openapi_blueprint_url_prefix: The url prefix of the OpenAPI blueprint. This
                prefix will append before all the OpenAPI-related paths (`sepc_path`,
                `docs_path`, etc.), defaults to `None`.
            json_errors: If `True`, APIFlask will return a JSON response for HTTP errors.
            enable_openapi: If `False`, will disable OpenAPI spec and API docs views.

        Other keyword arguments are directly passed to `flask.Flask`.

        *Version changed: 0.7.0*

        - Add `openapi_blueprint_url_prefix` argument.
        """
        super().__init__(
            import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path
        )

        # Set default config
        self.config.from_object('apiflask.settings')

        self.title = title
        self.version = version
        self.spec_path = spec_path
        self.docs_path = docs_path
        self.redoc_path = redoc_path
        self.docs_oauth2_redirect_path = docs_oauth2_redirect_path
        self.openapi_blueprint_url_prefix = openapi_blueprint_url_prefix
        self.enable_openapi = enable_openapi
        self.json_errors = json_errors

        self.spec_callback: t.Optional[SpecCallbackType] = None
        self.error_callback: ErrorCallbackType = self._error_handler  # type: ignore
        self.schema_name_resolver = self._schema_name_resolver

        self._spec: t.Optional[t.Union[dict, str]] = None
        self._register_openapi_blueprint()
        self._register_error_handlers()

    def _register_error_handlers(self) -> None:
        """Register default error handlers for HTTPError and WerkzeugHTTPException.

        *Version changed: 0.9.0*

        - Always pass an `HTTPError` instance to error handlers.
        """
        @self.errorhandler(HTTPError)  # type: ignore
        def handle_http_errors(
            error: HTTPError
        ) -> ResponseType:
            return self.error_callback(error)

        if self.json_errors:
            @self.errorhandler(WerkzeugHTTPException)  # type: ignore
            def handle_werkzeug_errors(
                error: WerkzeugHTTPException
            ) -> ResponseType:
                error = HTTPError(error.code, error.name)  # type: ignore
                return self.error_callback(error)

    def dispatch_request(self) -> ResponseType:
        """Overwrite the default dispatch method in Flask.

        With this overwrite, view arguments are passed as positional
        arguments so that the view function can intuitively accept the
        parameters (i.e., from top to bottom, from left to right).

        Examples:

        ```python
        @app.get('/pets/<name>/<int:pet_id>/<age>')  # -> name, pet_id, age
        @input(QuerySchema)  # -> query
        @output(PetSchema)  # -> pet
        def get_pet(name, pet_id, age, query, pet):
            pass
        ```

        From Flask, see the NOTICE file for license information.

        *Version added: 0.2.0*
        """
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule = req.url_rule
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if (  # pragma: no cover
            getattr(rule, "provide_automatic_options", False)
            and req.method == "OPTIONS"
        ):
            return self.make_default_options_response()  # pragma: no cover
        # otherwise dispatch to the handler for that endpoint
        view_function = self.view_functions[rule.endpoint]
        if hasattr(self, 'ensure_sync'):  # pragma: no cover
            view_function = self.ensure_sync(view_function)
        if rule.endpoint == 'static':
            # app static route only accepts keyword arguments, see flask#3762
            return view_function(**req.view_args)  # type: ignore
        else:
            return view_function(*req.view_args.values())  # type: ignore

    @staticmethod
    def _error_handler(
        error: HTTPError
    ) -> t.Union[t.Tuple[dict, int], t.Tuple[dict, int, t.Mapping[str, str]]]:
        """The default error handler.

        Arguments:
            status_code: The status code of the error (4XX and 5xx).
            message: The simple description of the error. If not provided,
                the reason phrase of the status code will be used.
            detail: The detailed information of the error, you can use it to
                provide the addition information such as custom error code,
                documentation URL, etc.
            headers: A dict of headers used in the error response.
        """
        body = {
            'detail': error.detail,
            'message': error.message,
            'status_code': error.status_code
        }
        return body, error.status_code, error.headers

    def error_processor(
        self,
        f: ErrorCallbackType
    ) -> ErrorCallbackType:
        """A decorator to register an error response processor function.

        The decorated callback function will be called in the following situations:

        - An validation error happened when parsing a request.
        - An exception triggered with [`HTTPError`][apiflask.exceptions.HTTPError]
        - An exception triggered with [`abort`][apiflask.exceptions.abort].

        If you have set the `json_errors` argument to `True` when creating the `app`
        instance, this callback function will also be used for normal HTTP errors,
        for example, 404 and 500 errors, etc. You can still register a specific error
        handler for a specific error code or exception with the
        `app.errorhandler(code_or_exection)` decorator, in that case, the return
        value of the error handler will be used as the response when the corresponding
        error or exception happened.

        The callback function must accept an error object as argument and return a valid
        response.

        Examples:

        ```python
        @app.error_processor
        def my_error_processor(error):
            return {
                'status_code': error.status_code,
                'message': error.message,
                'detail': error.detail
            }, error.status_code, error.headers
        ```

        The error object is an instance of [`HTTPError`][apiflask.exceptions.HTTPError],
        so you can get error information via it's attributes:

        - status_code: If the error triggered by validation error, the value will be
            400 (default) or the value you passed in config `VALIDATION_ERROR_STATUS_CODE`.
            If the error triggered by [`HTTPError`][apiflask.exceptions.HTTPError]
            or [`abort`][apiflask.exceptions.abort], it will be the status code
            you passed. Otherwise, it will be the status code set by Werkzueg when
            processing the request.
        - message: The error description for this error, either you passed or grab from
            Werkzeug.
        - detail: The detail of the error. When the validation error happened, it will
            be filled automatically in the following structure:

            ```python
            "<location>": {
                "<field_name>": ["<error_message>", ...],
                "<field_name>": ["<error_message>", ...],
                ...
            },
            "<location>": {
                ...
            },
            ...
            ```

            The value of `location` can be `json` (i.e., request body) or `query`
            (i.e., query string) depend on the place where the validation error
            happened.
        - headers: The value will be `None` unless you pass it in HTTPError or abort.

        If you want, you can rewrite the whole response body to anything you like:

        ```python
        @app.error_processor
        def my_error_processor(error):
            return {'error_detail': error.detail}, error.status_code, error.headers
        ```

        However, I would recommend keeping the `detail` in the response since it contains
        the detailed information about the validation error when the validation error
        happened.

        *Version changed: 0.7.0*

        - Support registering an async callback function.
        """
        if hasattr(self, 'ensure_sync'):  # pragma: no cover
            self.error_callback = self.ensure_sync(f)
        else:  # pragma: no cover
            self.error_callback = f
        return f

    def _register_openapi_blueprint(self) -> None:
        """Register a blueprint for OpenAPI support.

        The name of the blueprint is "openapi". This blueprint will hold the view
        functions for spec file, Swagger UI and Redoc.

        *Version changed: 0.7.0*

        - The format of the spec now rely on the `SPEC_FORMAT` config.
        """
        bp = Blueprint(
            'openapi',
            __name__,
            url_prefix=self.openapi_blueprint_url_prefix
        )

        if self.spec_path:
            @bp.route(self.spec_path)
            def spec() -> ResponseType:
                if self.config['SPEC_FORMAT'] == 'json':
                    response = jsonify(self._get_spec('json'))
                    response.mimetype = self.config['JSON_SPEC_MIMETYPE']
                    return response
                return self._get_spec('yaml'), 200, \
                    {'Content-Type': self.config['YAML_SPEC_MIMETYPE']}

        if self.docs_path:
            @bp.route(self.docs_path)
            def swagger_ui() -> str:
                return render_template_string(
                    swagger_ui_template,
                    title=self.title,
                    version=self.version,
                    oauth2_redirect_path=self.docs_oauth2_redirect_path
                )

            if self.docs_oauth2_redirect_path:
                @bp.route(self.docs_oauth2_redirect_path)
                def swagger_ui_oauth_redirect() -> str:
                    return render_template_string(swagger_ui_oauth2_redirect_template)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc() -> str:
                return render_template_string(
                    redoc_template,
                    title=self.title,
                    version=self.version
                )

        if self.enable_openapi and (
            self.spec_path or self.docs_path or self.redoc_path
        ):
            self.register_blueprint(bp)

    def _get_spec(
        self,
        spec_format: t.Optional[str] = None,
        force_update: bool = False
    ) -> t.Union[dict, str]:
        """Get the current OAS document file.

        This method will return the cached spec on the first call. If you want
        to get the latest spec, set the `force_update` to `True` or use the
        public attribute `app.spec`, which will always return the newly generated
        spec when you call it.

        If the config `SYNC_LOCAL_SPEC` is `True`, the local spec
        specified in config `LOCAL_SPEC_PATH` will be automatically updated
        when the spec changes.

        Arguments:
            spec_format: The format of the spec file, one of `'json'`, `'yaml'`
                and `'yml'`, defaults to the `SPEC_FORMAT` config.
            force_update: If ture, will generate the spec for every call instead
                of using the cache.

        *Version changed: 0.7.0*

        - The default format now rely on the `SPEC_FORMAT` config.
        - Support to sync local spec file.

        *Version changed: 0.7.1*

        - Rename the method name to `_get_spec`.
        - Add the `force_update` parameter.
        """
        if spec_format is None:
            spec_format = self.config['SPEC_FORMAT']
        if self._spec is None or force_update:
            if spec_format == 'json':
                self._spec = self._generate_spec().to_dict()
            else:
                self._spec = self._generate_spec().to_yaml()
            if self.spec_callback:
                self._spec = self.spec_callback(self._spec)  # type: ignore
        # sync local spec
        if self.config['SYNC_LOCAL_SPEC']:
            spec_path = self.config['LOCAL_SPEC_PATH']
            if spec_path is None:
                raise TypeError(
                    'The spec path (LOCAL_SPEC_PATH) should be a valid path string.'
                )
            spec: str
            if spec_format == 'json':
                spec = json.dumps(
                    self._spec, indent=self.config['LOCAL_SPEC_JSON_INDENT']
                )
            else:
                spec = str(self._spec)
            with open(spec_path, 'w') as f:
                f.write(spec)
        return self._spec  # type: ignore

    def spec_processor(self, f: SpecCallbackType) -> SpecCallbackType:
        """A decorator to register a spec handler callback function.

        You can register a function to update the spec. The callback function
        should accept the spec as an argument and return it in the end. The
        callback function will be called when generating the spec file.

        Examples:

        ```python
        @app.spec_processor
        def update_spec(spec):
            spec['info']['title'] = 'Updated Title'
            return spec
        ```

        Notice the format of the spec is depends on the the value of configuration
        variable `SPEC_FORMAT` (defaults to `'json'`):

        - `'json'` -> dict
        - `'yaml'` -> string

        *Version Changed: 0.7.0*

        - Support registering an async callback function.
        """
        if hasattr(self, 'ensure_sync'):  # pragma: no cover
            self.spec_callback = self.ensure_sync(f)
        else:  # pragma: no cover
            self.spec_callback = f
        return f

    @property
    def spec(self) -> t.Union[dict, str]:
        """Get the current OAS document file.

        This property will call `app._get_spec()` method and set the
        `force_update` parameter to `True`.

        *Version changed: 0.7.1*

        - Generate the spec on every call.
        """
        return self._get_spec(force_update=True)

    @staticmethod
    def _schema_name_resolver(schema: t.Type[Schema]) -> str:
        """Default schema name resovler."""
        name = schema.__class__.__name__
        if name.endswith('Schema'):
            name = name[:-6] or name
        if schema.partial:
            name += 'Update'
        return name

    def _make_info(self) -> dict:
        """Make OpenAPI info object."""
        info: dict
        if self.info:
            info = self.info
        else:
            info = {}
        if self.contact:
            info['contact'] = self.contact
        if self.license:
            info['license'] = self.license
        if self.terms_of_service:
            info['termsOfService'] = self.terms_of_service
        if self.description:
            info['description'] = self.description
        return info

    def _make_tags(self) -> t.List[t.Dict[str, t.Any]]:
        """Make OpenAPI tags object."""
        tags: t.Optional[TagsType] = self.tags
        if tags is not None:
            # convert simple tags list into standard OpenAPI tags
            if isinstance(tags[0], str):
                for index, tag_name in enumerate(tags):
                    tags[index] = {'name': tag_name}  # type: ignore
        else:
            tags: t.List[t.Dict[str, t.Any]] = []  # type: ignore
            if self.config['AUTO_TAGS']:
                # auto-generate tags from blueprints
                for blueprint_name, blueprint in self.blueprints.items():
                    if blueprint_name == 'openapi' or \
                       not hasattr(blueprint, 'enable_openapi') or \
                       not blueprint.enable_openapi:  # type: ignore
                        continue
                    tag: t.Dict[str, t.Any] = get_tag(blueprint, blueprint_name)  # type: ignore
                    tags.append(tag)  # type: ignore
        return tags  # type: ignore

    def _generate_spec(self) -> APISpec:
        """Generate the spec, return an instance of `apispec.APISpec`.

        *Version changed: 0.9.0*

        - Add base response customization support.

        *Version changed: 0.8.0*

        - Add automatic 404 response support.
        """
        kwargs: dict = {}
        if self.servers:
            kwargs['servers'] = self.servers
        if self.external_docs:
            kwargs['externalDocs'] = self.external_docs

        ma_plugin: MarshmallowPlugin = MarshmallowPlugin(
            schema_name_resolver=self.schema_name_resolver
        )
        spec: APISpec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version=self.config['OPENAPI_VERSION'],
            plugins=[ma_plugin],
            info=self._make_info(),
            tags=self._make_tags(),
            **kwargs
        )

        # configure flask-marshmallow URL types
        ma_plugin.converter.field_mapping[fields.URLFor] = ('string', 'url')
        ma_plugin.converter.field_mapping[fields.AbsoluteURLFor] = \
            ('string', 'url')
        if sqla is not None:  # pragma: no cover
            ma_plugin.converter.field_mapping[sqla.HyperlinkRelated] = \
                ('string', 'url')

        # security schemes
        auth_names: t.List[str] = []
        auth_schemes: t.List[HTTPAuthType] = []
        auth_blueprints: t.Dict[t.Optional[str], t.Dict[str, t.Any]] = {}

        def _update_auth_info(auth: HTTPAuthType) -> None:
            # update auth_schemes and auth_names
            auth_schemes.append(auth)
            auth_name: str = get_auth_name(auth, auth_names)
            auth_names.append(auth_name)

        # detect auth_required on before_request functions
        for blueprint_name, funcs in self.before_request_funcs.items():
            if blueprint_name is not None and \
               not self.blueprints[blueprint_name].enable_openapi:  # type: ignore
                continue
            for f in funcs:
                if hasattr(f, '_spec'):  # pragma: no cover
                    auth = f._spec.get('auth')  # type: ignore
                    if auth is not None and auth not in auth_schemes:
                        auth_blueprints[blueprint_name] = {
                            'auth': auth,
                            'roles': f._spec.get('roles')  # type: ignore
                        }
                        _update_auth_info(auth)
        # collect auth info
        for rule in self.url_map.iter_rules():
            view_func: ViewFuncType = self.view_functions[rule.endpoint]  # type: ignore
            if hasattr(view_func, '_spec'):
                auth = view_func._spec.get('auth')
                if auth is not None and auth not in auth_schemes:
                    _update_auth_info(auth)
            # method views
            if hasattr(view_func, '_method_spec'):
                for method_spec in view_func._method_spec.values():
                    auth = method_spec.get('auth')
                    if auth is not None and auth not in auth_schemes:
                        _update_auth_info(auth)

        security, security_schemes = get_security_and_security_schemes(
            auth_names, auth_schemes
        )
        for name, scheme in security_schemes.items():
            spec.components.security_scheme(name, scheme)

        # paths
        paths: t.Dict[str, t.Dict[str, t.Any]] = {}
        rules: t.List[t.Any] = sorted(
            list(self.url_map.iter_rules()), key=lambda rule: len(rule.rule)
        )
        for rule in rules:
            operations: t.Dict[str, t.Any] = {}
            view_func: ViewFuncType = self.view_functions[rule.endpoint]  # type: ignore
            # skip endpoints from openapi blueprint and the built-in static endpoint
            if rule.endpoint.startswith('openapi') or \
               rule.endpoint.startswith('static'):
                continue
            blueprint_name: t.Optional[str] = None  # type: ignore
            if '.' in rule.endpoint:
                blueprint_name: str = rule.endpoint.rsplit('.', 1)[0]  # type: ignore
                blueprint = self.blueprints[blueprint_name]  # type: ignore
                if not hasattr(blueprint, 'enable_openapi') or \
                   not blueprint.enable_openapi:  # type: ignore
                    continue
            # add a default 200 response for bare views
            if not hasattr(view_func, '_spec'):
                if self.config['AUTO_200_RESPONSE']:
                    view_func._spec = {'response': default_response}
                else:
                    continue  # pragma: no cover
            # method views
            if hasattr(view_func, '_method_spec'):
                skip = True
                for method, method_spec in view_func._method_spec.items():
                    if method_spec.get('no_spec'):
                        if self.config['AUTO_200_RESPONSE']:
                            view_func._method_spec[method]['response'] = default_response
                            skip = False
                    else:
                        skip = False
                if skip:
                    continue
            # skip views flagged with @doc(hide=True)
            if view_func._spec.get('hide'):
                continue

            # operation tags
            operation_tags: t.Optional[t.List[str]] = None
            if view_func._spec.get('tags'):
                operation_tags = view_func._spec.get('tags')
            else:
                # use blueprint name as tag
                if self.tags is None and self.config['AUTO_TAGS'] and \
                   blueprint_name is not None:
                    blueprint = self.blueprints[blueprint_name]
                    operation_tags = \
                        get_operation_tags(blueprint, blueprint_name)  # type: ignore

            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if method not in rule.methods:
                    continue
                # method views
                if hasattr(view_func, '_method_spec'):
                    if method not in view_func._method_spec:
                        continue  # pragma: no cover
                    view_func._spec = view_func._method_spec[method]

                    if view_func._spec.get('no_spec') and \
                       not self.config['AUTO_200_RESPONSE']:
                        continue
                    if view_func._spec.get('generated_summary') and \
                       not self.config['AUTO_OPERATION_SUMMARY']:
                        view_func._spec['summary'] = ''
                    if view_func._spec.get('generated_description') and \
                       not self.config['AUTO_OPERATION_DESCRIPTION']:
                        view_func._spec['description'] = ''
                    if view_func._spec.get('hide'):
                        continue
                    if view_func._spec.get('tags'):
                        operation_tags = view_func._spec.get('tags')
                    else:
                        if self.tags is None and self.config['AUTO_TAGS'] and \
                           blueprint_name is not None:
                            blueprint = self.blueprints[blueprint_name]
                            operation_tags = \
                                get_operation_tags(blueprint, blueprint_name)  # type: ignore

                operation: t.Dict[str, t.Any] = {
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                    ],
                    'responses': {},
                }
                if operation_tags:
                    operation['tags'] = operation_tags

                # summary
                if view_func._spec.get('summary'):
                    operation['summary'] = view_func._spec.get('summary')
                else:
                    # auto-generate summary from dotstring or view function name
                    if self.config['AUTO_OPERATION_SUMMARY']:
                        operation['summary'] = get_path_summary(view_func)  # type: ignore

                # description
                if view_func._spec.get('description'):
                    operation['description'] = view_func._spec.get('description')
                else:
                    # auto-generate description from dotstring
                    if self.config['AUTO_OPERATION_DESCRIPTION']:
                        docs = [
                            line.strip() for line in (view_func.__doc__ or '').strip().split('\n')
                        ]
                        if len(docs) > 1:
                            # use the remain lines of docstring as description
                            operation['description'] = '\n'.join(docs[1:]).strip()

                # deprecated
                if view_func._spec.get('deprecated'):
                    operation['deprecated'] = view_func._spec.get('deprecated')

                # responses
                if view_func._spec.get('response'):
                    schema = view_func._spec.get('response')['schema']
                    base_schema: OpenAPISchemaType = self.config['BASE_RESPONSE_SCHEMA']
                    if base_schema is not None:
                        base_schema_spec: dict
                        if isinstance(base_schema, type):
                            base_schema_spec = ma_plugin.converter.schema2jsonschema(
                                base_schema()
                            )
                        elif isinstance(base_schema, dict):
                            base_schema_spec = base_schema
                        else:
                            raise TypeError(_bad_schema_message)
                        data_key: str = self.config['BASE_RESPONSE_DATA_KEY']
                        if data_key not in base_schema_spec['properties']:
                            raise RuntimeError(
                                f'The data key "{data_key}" is not found in'
                                ' the base response schema spec.'
                            )
                        base_schema_spec['properties'][data_key] = schema
                        schema = base_schema_spec

                    status_code: str = str(view_func._spec.get('response')['status_code'])
                    description: str = view_func._spec.get('response')['description'] or \
                        self.config['SUCCESS_DESCRIPTION']
                    example = view_func._spec.get('response')['example']
                    examples = view_func._spec.get('response')['examples']
                    add_response(
                        operation, status_code, schema, description, example, examples
                    )
                else:
                    # add a default 200 response for views without using @output
                    # or @doc(responses={...})
                    if not view_func._spec.get('responses') and self.config['AUTO_200_RESPONSE']:
                        add_response(
                            operation, '200', {}, self.config['SUCCESS_DESCRIPTION']
                        )

                # add validation error response
                if self.config['AUTO_VALIDATION_ERROR_RESPONSE'] and \
                   (view_func._spec.get('body') or view_func._spec.get('args')):
                    status_code: str = str(  # type: ignore
                        self.config['VALIDATION_ERROR_STATUS_CODE']
                    )
                    description: str = self.config[  # type: ignore
                        'VALIDATION_ERROR_DESCRIPTION'
                    ]
                    schema: SchemaType = self.config['VALIDATION_ERROR_SCHEMA']  # type: ignore
                    add_response_with_schema(
                        spec, operation, status_code, schema, 'ValidationError', description
                    )

                # add authentication error response
                if self.config['AUTO_AUTH_ERROR_RESPONSE'] and \
                   (view_func._spec.get('auth') or (
                       blueprint_name is not None and blueprint_name in auth_blueprints
                   )):
                    status_code: str = str(  # type: ignore
                        self.config['AUTH_ERROR_STATUS_CODE']
                    )
                    description: str = self.config['AUTH_ERROR_DESCRIPTION']  # type: ignore
                    schema: SchemaType = self.config['HTTP_ERROR_SCHEMA']  # type: ignore
                    add_response_with_schema(
                        spec, operation, status_code, schema, 'HTTPError', description
                    )

                # add 404 error response
                if self.config['AUTO_404_RESPONSE'] and rule.arguments:
                    description: str = self.config['NOT_FOUND_DESCRIPTION']  # type: ignore
                    schema: SchemaType = self.config['HTTP_ERROR_SCHEMA']  # type: ignore
                    add_response_with_schema(
                        spec, operation, '404', schema, 'HTTPError', description
                    )

                if view_func._spec.get('responses'):
                    responses: t.Union[t.List[int], t.Dict[int, str]] \
                        = view_func._spec.get('responses')
                    if isinstance(responses, list):
                        responses: t.Dict[int, str] = {}  # type: ignore
                        for status_code in view_func._spec.get('responses'):
                            responses[  # type: ignore
                                status_code
                            ] = get_reason_phrase(int(status_code), '')
                    for status_code, description in responses.items():  # type: ignore
                        status_code: str = str(status_code)  # type: ignore
                        if status_code in operation['responses']:
                            if not isinstance(
                                view_func._spec.get('responses'), list
                            ):  # pragma: no cover
                                operation['responses'][status_code]['description'] = description
                            continue
                        if status_code.startswith('4') or status_code.startswith('5'):
                            # add error response schema for error responses
                            schema: SchemaType = self.config['HTTP_ERROR_SCHEMA']  # type: ignore
                            add_response_with_schema(
                                spec, operation, status_code, schema, 'HTTPError', description
                            )
                        else:
                            add_response(operation, status_code, {}, description)

                # requestBody
                if view_func._spec.get('body'):
                    operation['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': view_func._spec['body'],
                            }
                        }
                    }
                    if view_func._spec.get('body_example'):
                        example = view_func._spec.get('body_example')
                        operation['requestBody']['content'][
                            'application/json']['example'] = example
                    if view_func._spec.get('body_examples'):
                        examples = view_func._spec.get('body_examples')
                        operation['requestBody']['content'][
                            'application/json']['examples'] = examples

                # security
                # app-wide auth
                if None in auth_blueprints:
                    operation['security'] = [{
                        security[auth_blueprints[None]['auth']]:
                            auth_blueprints[None]['roles']
                    }]

                # blueprint-wide auth
                if blueprint_name is not None and blueprint_name in auth_blueprints:
                    operation['security'] = [{
                        security[auth_blueprints[blueprint_name]['auth']]:
                            auth_blueprints[blueprint_name]['roles']
                    }]

                # view-wide auth
                if view_func._spec.get('auth'):
                    operation['security'] = [{
                        security[view_func._spec['auth']]: view_func._spec['roles']
                    }]

                operations[method.lower()] = operation

            # parameters
            path_arguments: t.Iterable = re.findall(r'<(([^<:]+:)?([^>]+))>', rule.rule)
            if path_arguments:
                arguments: t.List[t.Dict[str, str]] = []
                for _, argument_type, argument_name in path_arguments:
                    argument = get_argument(argument_type, argument_name)
                    arguments.append(argument)

                for _method, operation in operations.items():
                    operation['parameters'] = arguments + operation['parameters']

            path: str = re.sub(r'<([^<:]+:)?', '{', rule.rule).replace('>', '}')
            if path not in paths:
                paths[path] = operations
            else:
                paths[path].update(operations)

        for path, operations in paths.items():
            # sort by method before adding them to the spec
            sorted_operations: t.Dict[str, t.Any] = {}
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in operations:
                    sorted_operations[method] = operations[method]
            spec.path(path=path, operations=sorted_operations)

        return spec
