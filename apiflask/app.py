from typing import Iterable, Union, List, Optional, Type, Tuple, Any, Dict
import re
import sys

from flask import Flask
from flask import Blueprint
from flask import render_template
from flask.config import ConfigAttribute
from flask.globals import _request_ctx_stack
from werkzeug.exceptions import HTTPException as WerkzeugHTTPException
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_marshmallow import fields
try:
    from flask_marshmallow import sqla
except ImportError:
    sqla = None

from .exceptions import HTTPError
from .exceptions import default_error_handler
from .utils import route_shortcuts
from .utils import get_reason_phrase
from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .schemas import Schema
from .types import ResponseType
from .types import ErrorCallbackType
from .types import SpecCallbackType


@route_shortcuts
class APIFlask(Flask):
    """The `Flask` object with some web API support.

    Examples:

    ```python
    from apiflask import APIFlask

    app = APIFlask(__name__)
    ```

    Attributes:
        description: The description of the API (openapi.info.description).
            This attribute can also be configured from the config with the
            `DESCRIPTION` configuration key. Defaults to `None`.
        tags: The tags of the OpenAPI spec documentation (openapi.tags), accepts a
            list of dicts. You can also pass a simple list contains the tag name:

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
        terms_of_service: The terms of service URL of the API
            (openapi.info.termsOfService). Example:

            ```python
            app.terms_of_service = "http://example.com/terms/"
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
            Example:

            ```python
            def my_error_handler(status_code, message, detail, headers):
                return {
                    'status_code': status_code,
                    'message': message,
                    'detail': detail
                }, status_code, headers

            app.error_processor = my_error_handler
            ```
    """
    description: Optional[str] = ConfigAttribute('DESCRIPTION')  # type: ignore
    tags: Optional[Union[List[str], List[Dict[str, str]]]
                   ] = ConfigAttribute('TAGS')  # type: ignore
    contact: Optional[Dict[str, str]] = ConfigAttribute('CONTACT')  # type: ignore
    license: Optional[Dict[str, str]] = ConfigAttribute('LICENSE')  # type: ignore
    servers: Optional[List[Dict[str, str]]] = ConfigAttribute('SERVERS')  # type: ignore
    external_docs: Optional[Dict[str, str]] = ConfigAttribute('EXTERNAL_DOCS')  # type: ignore
    terms_of_service: Optional[str] = ConfigAttribute('TERMS_OF_SERVICE')  # type: ignore

    def __init__(
        self,
        import_name: str,
        title: str = 'APIFlask',
        version: str = '0.1.0',
        spec_path: str = '/openapi.json',
        docs_path: str = '/docs',
        docs_oauth2_redirect_path: str = '/docs/oauth2-redirect',
        redoc_path: str = '/redoc',
        json_errors: bool = True,
        enable_openapi: bool = True,
        static_url_path: Optional[str] = None,
        static_folder: str = 'static',
        static_host: Optional[str] = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str = 'templates',
        instance_path: Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: Optional[str] = None
    ) -> None:
        """Make a Flask app instance.

        Arguments:
            import_name: The name of the application package, usually
                `__name__`. This helps locate the `root_path` for the
                application.
            title: The title of the API (openapi.info.title), defaults to "APIFlask".
                You can change it to the name of your API (e.g. "Pet API").
            version: The version of the API (openapi.info.version), defaults to "1.0.0".
            spec_path: The path to OpenAPI Spec documentation. It
                defaults to `/openapi.json`, if the path end with `.yaml`
                or `.yml`, the YAML format of the OAS will be returned.
            docs_path: The path to Swagger UI documentation, defaults to `/docs`.
            docs_oauth2_redirect_path: The path to Swagger UI OAuth redirect.
            redoc_path: The path to Redoc documentation, defaults to `/redoc`.
            json_errors: If True, APIFlask will return a JSON response for HTTP errors.
            enable_openapi: If False, will disable OpenAPI spec and API docs views.

        Other keyword arguments are directly pass to `flask.Flask`.
        """
        super(APIFlask, self).__init__(
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
        self.enable_openapi = enable_openapi
        self.json_errors = json_errors

        self.spec_callback: Optional[SpecCallbackType] = None  # type: ignore
        self.error_callback: ErrorCallbackType = default_error_handler  # type: ignore
        self._spec: Optional[Union[dict, str]] = None
        self._register_openapi_blueprint()

        @self.errorhandler(HTTPError)
        def handle_http_error(
            error: HTTPError
        ) -> ResponseType:
            return self.error_callback(
                error.status_code,
                error.message,
                error.detail,
                error.headers  # type: ignore
            )

        if self.json_errors:
            @self.errorhandler(WerkzeugHTTPException)
            def handle_werkzeug_errrors(
                error: WerkzeugHTTPException
            ) -> ResponseType:
                return self.error_callback(
                    error.code,  # type: ignore
                    error.name,
                    detail=None,  # type: ignore
                    headers=None  # type: ignore
                )

    def dispatch_request(self) -> ResponseType:
        """Overwrite the default dispatch method to pass view arguments as positional
        arguments. With this overwrite, the view function can accept the parameters in
        a intuitive way (from top to bottom, from left to right).

        Examples:

        ```python
        @app.get('/pets/<name>/<int:pet_id>/<age>')  # -> name, pet_id, age
        @input(QuerySchema)  # -> query
        @output(PetSchema)  # -> pet
        def get_pet(name, pet_id, age, query, pet):
            pass
        ```

        From Flask, see NOTICE file for license informaiton.

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
        return self.view_functions[rule.endpoint](*req.view_args.values())

    def error_processor(
        self,
        f: ErrorCallbackType
    ) -> ErrorCallbackType:
        """A decorator used to register a error handler callback function.

        The callback function will be called when validation error hanppend when
        parse a request or an exception triggerd with exceptions.HTTPError or
        :func:`exceptions.abort`. It must accept four positional arguments (i.e.
        `status_code, message, detail, headers`) and return a valid response.

        Examples:

        ```python
        @app.error_processor
        def my_error_handler(status_code, message, detail, headers):
            return {
                'status_code': status_code,
                'message': message,
                'detail': detail
            }, status_code, headers
        ```

        The arguments are:

        - status_code: If the error triggerd by validation error, the value will be
            400 (default) or the value you passed in config `VALIDATION_ERROR_STATUS_CODE`.
            If the error triggerd by HTTP, it will be the status code you passed.
            Otherwise, it will be the status code set by Werkzueg when processing the request.
        - message: The error description for this error, either you passed or grab from Werkzeug.
        - detail: The detail of the error, it will be filled when validation error happaned, the
            structure will be:

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

            The value of `location` can be `json` (i.e. request body) or `query`
            (i.e. query string) depend on the palace the validation error happened.
        - headers: The value will be None unless you pass it in HTTPError or abort.

        If you want, you can rewrite the whole response body to anything you like:

        ```python
        @app.errorhandler_callback
        def my_error_handler(status_code, message, detail, headers):
            return {'error_detail': detail}, status_code, headers
        ```

        However, I would recommend to keep the `detail` since it contains the detail
        information about the validation error.
        """
        self.error_callback = f
        return f

    def _register_openapi_blueprint(self) -> None:
        """Register a bluepint for OpenAPI support.

        The name of the blueprint is "openapi". This blueprint will hold the view
        functions for spec file, Swagger UI and Redoc.
        """
        bp = Blueprint(
            'openapi',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/apiflask'
        )

        if self.spec_path:
            @bp.route(self.spec_path)
            def spec() -> Union[
                Union[Dict[Any, Any], str],
                Tuple[Union[Dict[Any, Any], str], int, Dict[str, str]]
            ]:
                if self.spec_path.endswith('.yaml') or \
                   self.spec_path.endswith('.yml'):
                    # YAML spec
                    return self.get_spec('yaml'), 200, \
                        {'Content-Type': 'text/vnd.yaml'}
                else:
                    # JSON spec
                    return self.get_spec('json')

        if self.docs_path:
            @bp.route(self.docs_path)
            def swagger_ui() -> str:
                return render_template('apiflask/swagger_ui.html',
                                       title=self.title, version=self.version)

            if self.docs_oauth2_redirect_path:
                @bp.route(self.docs_oauth2_redirect_path)
                def swagger_ui_oauth_redirect() -> str:
                    return render_template('apiflask/swagger_ui_oauth2_redirect.html',
                                           title=self.title, version=self.version)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc() -> str:
                return render_template('apiflask/redoc.html',
                                       title=self.title, version=self.version)

        if self.enable_openapi and (
            self.spec_path or self.docs_path or self.redoc_path
        ):
            self.register_blueprint(bp)

    def get_spec(self, spec_format: Optional[str] = None) -> Union[dict, str]:
        """
        Get the current OAS document file.

        Arguments:
            spec_format: The format of the spec file, one of `'json'` and `'yaml'`,
                defaults to `None`. If not set, the value of configuration variable
                `SPEC_FORMAT` will be used (defaults to `'json'`).
        """
        if spec_format is None:
            spec_format = self.config['SPEC_FORMAT'].lower()
        if self._spec is None:
            if spec_format == 'json':
                self._spec = self._generate_spec().to_dict()
            else:
                self._spec = self._generate_spec().to_yaml()
            if self.spec_callback:
                self._spec = self.spec_callback(self._spec)
        return self._spec

    def spec_processor(self, f: SpecCallbackType) -> SpecCallbackType:
        """A decorator used to register a spec handler callback function.

        You can register a function to update the spec. The callback function
        should accept the spec as argument and return it in the end. The callback
        function will be called when generating the spec file.

        Examples:

        ```python
        @app.spec_processor
        def update_spec(spec):
            spec['title'] = 'Updated Title'
            return spec
        ```

        Notice the format of the spec is depends on the the value of configuration
        variable `SPEC_FORMAT` (defaults to `'json'`):

        - `'json'` -> dictionary
        - `'yaml'` -> string
        """
        self.spec_callback = f
        return f

    @property
    def spec(self) -> Union[dict, str]:
        """Get the current OAS document file.

        This property will call [get_spec][apiflask.APIFlask.get_spec] method.
        """
        return self.get_spec()

    def _generate_spec(self) -> APISpec:
        """Generate the spec, return an instance of `apispec.APISpec`.
        """
        def resolver(schema: Schema) -> str:
            name = schema.__class__.__name__
            if name.endswith('Schema'):
                name = name[:-6] or name
            if schema.partial:
                name += 'Update'
            return name

        # info object
        info: dict = {}
        if self.contact:
            info['contact'] = self.contact
        if self.license:
            info['license'] = self.license
        if self.terms_of_service:
            info['termsOfService'] = self.terms_of_service
        if self.description:
            info['description'] = self.description
        else:
            # auto-generate info.description from module doc
            if self.config['AUTO_DESCRIPTION']:
                module_name = self.import_name
                while module_name:
                    module = sys.modules[module_name]
                    if module.__doc__:
                        info['description'] = module.__doc__.strip()
                        break
                    if '.' not in module_name:
                        module_name = '.' + module_name
                    module_name = module_name.rsplit('.', 1)[0]

        # tags
        tags: Optional[Union[List[str], List[Dict[str, Any]]]] = self.tags
        if tags is not None:
            # Convert simple tags list into standard OpenAPI tags
            if isinstance(tags[0], str):
                for index, tag in enumerate(tags):
                    tags[index] = {'name': tag}  # type: ignore
        else:
            tags: List[str] = []  # type: ignore
            if self.config['AUTO_TAGS']:
                # auto-generate tags from blueprints
                for name, blueprint in self.blueprints.items():
                    if name == 'openapi' or name in self.config['DOCS_HIDE_BLUEPRINTS']:
                        continue
                    if hasattr(blueprint, 'tag') and blueprint.tag is not None:
                        if isinstance(blueprint.tag, dict):
                            tag = blueprint.tag
                        else:
                            tag = {'name': blueprint.tag}
                    else:
                        tag = {'name': name.title()}
                        module = sys.modules[blueprint.import_name]
                        if module.__doc__:
                            tag['description'] = module.__doc__.strip()
                    tags.append(tag)  # type: ignore

        # additional fields
        kwargs: dict = {}
        if self.servers:
            kwargs['servers'] = self.servers
        if self.external_docs:
            kwargs['externalDocs'] = self.external_docs

        ma_plugin: Type[MarshmallowPlugin] = MarshmallowPlugin(schema_name_resolver=resolver)
        spec: Type[APISpec] = APISpec(
            title=self.title,
            version=self.version,
            openapi_version='3.0.3',
            plugins=[ma_plugin],
            info=info,
            tags=tags,
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
        auth_schemes: List[Union[Type[HTTPBasicAuth], Type[HTTPTokenAuth]]] = []
        auth_names: List[str] = []
        auth_blueprints: Dict[str, Dict[str, Any]] = {}

        def add_auth_schemes_and_names(
            auth: Union[Type[HTTPBasicAuth], Type[HTTPTokenAuth]]
        ) -> None:
            auth_schemes.append(auth)
            if isinstance(auth, HTTPBasicAuth):
                name = 'BasicAuth'
            elif isinstance(auth, HTTPTokenAuth):
                if auth.scheme == 'Bearer' and auth.header is None:
                    name = 'BearerAuth'
                else:
                    name = 'ApiKeyAuth'
            else:
                raise RuntimeError('Unknown authentication scheme')
            if name in auth_names:
                v = 2
                new_name = f'{name}_{v}'
                while new_name in auth_names:
                    v += 1
                    new_name = f'{name}_{v}'
                name = new_name
            auth_names.append(name)

        # detect auth_required on before_request functions
        for blueprint_name, funcs in self.before_request_funcs.items():
            for f in funcs:
                if hasattr(f, '_spec'):  # pragma: no cover
                    auth = f._spec.get('auth')  # type: ignore
                    if auth is not None and auth not in auth_schemes:
                        auth_blueprints[blueprint_name] = {  # type: ignore
                            'auth': auth,
                            'roles': f._spec.get('roles')  # type: ignore
                        }
                        add_auth_schemes_and_names(auth)

        for rule in self.url_map.iter_rules():
            view_func = self.view_functions[rule.endpoint]
            if hasattr(view_func, '_spec'):
                auth = view_func._spec.get('auth')
                if auth is not None and auth not in auth_schemes:
                    add_auth_schemes_and_names(auth)

        security: Dict[Union[Type[HTTPBasicAuth], Type[HTTPTokenAuth]], str] = {}
        security_schemes: Dict[str, Dict[str, str]] = {}
        for name, auth in zip(auth_names, auth_schemes):
            security[auth] = name
            if isinstance(auth, HTTPTokenAuth):
                if auth.scheme == 'Bearer' and auth.header is None:
                    security_schemes[name] = {
                        'type': 'http',
                        'scheme': 'Bearer',
                    }
                else:
                    security_schemes[name] = {
                        'type': 'apiKey',
                        'name': auth.header,
                        'in': 'header',
                    }
            else:
                security_schemes[name] = {
                    'type': 'http',
                    'scheme': 'Basic',
                }

            if hasattr(auth, 'description') and auth.description is not None:
                security_schemes[name]['description'] = auth.description

        for name, scheme in security_schemes.items():
            spec.components.security_scheme(name, scheme)

        # paths
        paths: Dict[str, Dict[str, Any]] = {}
        # rules: List[Any] = list(self.url_map.iter_rules())
        rules: List[Any] = sorted(
            list(self.url_map.iter_rules()), key=lambda rule: len(rule.rule)
        )
        for rule in rules:
            operations: Dict[str, Any] = {}
            view_func = self.view_functions[rule.endpoint]
            # skip endpoints from openapi blueprint and the built-in static endpoint
            if rule.endpoint.startswith('openapi') or \
               rule.endpoint.startswith('static'):
                continue
            # skip endpoints from blueprints in config DOCS_HIDE_BLUEPRINTS list
            blueprint_name: Optional[str] = None  # type: ignore
            if '.' in rule.endpoint:
                blueprint_name = rule.endpoint.split('.', 1)[0]
                if blueprint_name in self.config['DOCS_HIDE_BLUEPRINTS']:
                    continue
            # add a default 200 response for bare views
            default_response = {
                'schema': {}, 'status_code': 200, 'description': None, 'example': None
            }
            if not hasattr(view_func, '_spec'):
                if self.config['AUTO_200_RESPONSE']:
                    view_func._spec = {'response': default_response}
                else:
                    continue  # pragma: no cover
            # skip views flagged with @doc(hide=True)
            if view_func._spec.get('hide'):
                continue

            # tag
            operation_tags: Optional[Union[str, List[str]]] = None
            if view_func._spec.get('tag'):
                operation_tags = view_func._spec.get('tag')
            else:
                # if tag not set, try to use blueprint name as tag
                if self.tags is None and self.config['AUTO_TAGS'] and blueprint_name is not None:
                    blueprint = self.blueprints[blueprint_name]
                    if hasattr(blueprint, 'tag') and blueprint.tag is not None:
                        if isinstance(blueprint.tag, dict):
                            operation_tags = blueprint.tag['name']
                        else:
                            operation_tags = blueprint.tag
                    else:
                        operation_tags = blueprint_name.title()

            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if method not in rule.methods:
                    continue
                operation: Dict[str, Any] = {
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                    ],
                    'responses': {},
                }
                if operation_tags:
                    if isinstance(operation_tags, list):
                        operation['tags'] = operation_tags
                    else:
                        operation['tags'] = [operation_tags]

                # summary
                if view_func._spec.get('summary'):
                    operation['summary'] = view_func._spec.get('summary')
                else:
                    # auto-generate summary from dotstring or view function name
                    if self.config['AUTO_PATH_SUMMARY']:
                        docs = (view_func.__doc__ or '').strip().split('\n')
                        if docs[0]:
                            # Use the first line of docstring as summary
                            operation['summary'] = docs[0]
                        else:
                            # Use the function name as summary
                            operation['summary'] = ' '.join(
                                view_func.__name__.split('_')).title()

                # description
                if view_func._spec.get('description'):
                    operation['description'] = view_func._spec.get('description')
                else:
                    # auto-generate description from dotstring
                    if self.config['AUTO_PATH_DESCRIPTION']:
                        docs = (view_func.__doc__ or '').strip().split('\n')
                        if len(docs) > 1:
                            # Use the remain lines of docstring as description
                            operation['description'] = '\n'.join(docs[1:]).strip()

                # deprecated
                if view_func._spec.get('deprecated'):
                    operation['deprecated'] = view_func._spec.get('deprecated')

                # responses
                descriptions: Dict[str, str] = {
                    '200': self.config['DEFAULT_200_DESCRIPTION'],
                    '201': self.config['DEFAULT_201_DESCRIPTION'],
                    '204': self.config['DEFAULT_204_DESCRIPTION'],
                }

                def add_response(
                    status_code: str,
                    schema: Union[Schema, dict],
                    description: str,
                    example: Optional[Any] = None
                ) -> None:
                    operation['responses'][status_code] = {
                        'content': {
                            'application/json': {
                                'schema': schema
                            }
                        }
                    }
                    operation['responses'][status_code]['description'] = description
                    if example is not None:
                        operation['responses'][status_code]['content'][
                            'application/json']['example'] = example

                def add_response_with_schema(
                    status_code: str,
                    schema: Union[Schema, dict],
                    schema_name: str,
                    description: str
                ) -> None:
                    if isinstance(schema, type):
                        schema = schema()
                        add_response(status_code, schema, description)
                    elif isinstance(schema, dict):
                        if schema_name not in spec.components.schemas:
                            spec.components.schema(schema_name, schema)
                        schema_ref = {'$ref': f'#/components/schemas/{schema_name}'}
                        add_response(status_code, schema_ref, description)
                    else:
                        raise RuntimeError(
                            'The schema must be a Marshamallow schema \
                            class or an OpenAPI schema dict.'
                        )

                if view_func._spec.get('response'):
                    status_code: str = str(view_func._spec.get('response')['status_code'])
                    schema = view_func._spec.get('response')['schema']
                    description: str = view_func._spec.get('response')['description'] or \
                        descriptions.get(status_code, self.config['DEFAULT_2XX_DESCRIPTION'])
                    example = view_func._spec.get('response')['example']
                    add_response(status_code, schema, description, example)
                else:
                    # add a default 200 response for views without using @output
                    # or @doc(responses={...})
                    if not view_func._spec.get('responses') and self.config['AUTO_200_RESPONSE']:
                        add_response('200', {}, descriptions['200'])

                # add validation error response
                if self.config['AUTO_VALIDATION_ERROR_RESPONSE']:
                    if view_func._spec.get('body') or view_func._spec.get('args'):
                        status_code: str = str(  # type: ignore
                            self.config['VALIDATION_ERROR_STATUS_CODE']
                        )
                        description: str = self.config[  # type: ignore
                            'VALIDATION_ERROR_DESCRIPTION'
                        ]
                        schema: Union[  # type: ignore
                            Schema, dict
                        ] = self.config['VALIDATION_ERROR_SCHEMA']
                        add_response_with_schema(
                            status_code, schema, 'ValidationError', description
                        )

                # add authorization error response
                if self.config['AUTO_AUTH_ERROR_RESPONSE']:
                    if view_func._spec.get('auth') or (
                        blueprint_name is not None and blueprint_name in auth_blueprints
                    ):
                        status_code: str = str(  # type: ignore
                            self.config['AUTH_ERROR_STATUS_CODE']
                        )
                        description: str = self.config['AUTH_ERROR_DESCRIPTION']  # type: ignore
                        schema: Union[  # type: ignore
                            Schema, dict
                        ] = self.config['AUTH_ERROR_SCHEMA']
                        add_response_with_schema(
                            status_code, schema, 'AuthorizationError', description
                        )

                if view_func._spec.get('responses'):
                    responses: Union[List[int], Dict[int, str]] \
                        = view_func._spec.get('responses')
                    if isinstance(responses, list):
                        responses: Dict[int, str] = {}  # type: ignore
                        for status_code in view_func._spec.get('responses'):
                            responses[  # type: ignore
                                status_code
                            ] = get_reason_phrase(int(status_code))
                    for status_code, description in responses.items():  # type: ignore
                        status_code: str = str(status_code)  # type: ignore
                        if status_code in operation['responses']:
                            continue
                        if self.config['AUTO_HTTP_ERROR_RESPONSE'] and (
                            status_code.startswith('4') or
                            status_code.startswith('5')  # type: ignore
                        ):
                            schema: Union[  # type: ignore
                                Schema, dict
                            ] = self.config['HTTP_ERROR_SCHEMA']
                            add_response_with_schema(
                                status_code, schema, 'HTTPError', description
                            )
                        else:
                            add_response(status_code, {}, description)

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
                        operation['requestBody']['content'][
                            'application/json']['example'] = view_func._spec.get('body_example')

                # security
                if blueprint_name is not None and blueprint_name in auth_blueprints:
                    operation['security'] = [{
                        security[auth_blueprints[blueprint_name]['auth']]:
                            auth_blueprints[blueprint_name]['roles']
                    }]

                if view_func._spec.get('auth'):
                    operation['security'] = [{
                        security[view_func._spec['auth']]: view_func._spec['roles']
                    }]

                operations[method.lower()] = operation

            # parameters
            path_arguments: Iterable = re.findall(r'<(([^<:]+:)?([^>]+))>', rule.rule)
            if path_arguments:
                arguments: List[Dict[str, str]] = []
                for _, argument_type, argument_name in path_arguments:
                    argument = {
                        'in': 'path',
                        'name': argument_name,
                    }
                    if argument_type == 'int:':
                        argument['schema'] = {'type': 'integer'}
                    elif argument_type == 'float:':
                        argument['schema'] = {'type': 'number'}
                    else:
                        argument['schema'] = {'type': 'string'}
                    arguments.append(argument)

                for method, operation in operations.items():
                    operation['parameters'] = arguments + operation['parameters']

            path: str = re.sub(r'<([^<:]+:)?', '{', rule.rule).replace('>', '}')
            if path not in paths:
                paths[path] = operations
            else:
                paths[path].update(operations)

        for path, operations in paths.items():
            # sort by method before adding them to the spec
            sorted_operations: Dict[str, Any] = {}
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in operations:
                    sorted_operations[method] = operations[method]
            spec.path(path=path, operations=sorted_operations)

        return spec
