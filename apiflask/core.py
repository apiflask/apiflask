from json import dumps
import re
import sys

from flask import Flask
from flask.globals import _request_ctx_stack
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Blueprint, render_template
from flask_marshmallow import fields
from werkzeug.datastructures import ImmutableDict
try:
    from flask_marshmallow import sqla
except ImportError:
    sqla = None
try:
    from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
except ImportError:  # pragma: no cover
    HTTPBasicAuth = None
    HTTPTokenAuth = None

from .exceptions import HTTPException
from .schemas import validation_error_response_schema


class APIFlask(Flask):

    api_default_config = ImmutableDict(
        {
            'OPENAPI_TITLE': 'APIFlask',
            'OPENAPI_VERSION': '1.0.0',
            'OPENAPI_SPEC_PATH': '/openapi.json',
            'SWAGGER_UI_PATH': '/docs',
            'REDOC_PATH': '/redoc',
            'OPENAPI_TAGS': None,
            '200_RESPONSE_DESCRIPTION': 'Successful response',
            '204_RESPONSE_DESCRIPTION': 'Empty response',
            'VALIDATION_ERROR_CODE': 400,
            'VALIDATION_ERROR_DESCRIPTION': 'Validation error',
            'HANDLE_BASIC_ERRORS': True
        }
    )

    def __init__(self, import_name, **kwargs):
        super(APIFlask, self).__init__(import_name, **kwargs)

        # set default config
        self.config.update(self.api_default_config)

        self.apispec_callback = None
        self.error_handler_callback = self.default_error_handler
        self._apispec = None

        bp = Blueprint('apiflask', __name__, template_folder='templates')

        if self.apispec_path:
            @bp.route(self.apispec_path)
            def json():
                return dumps(self.apispec), 200, \
                    {'Content-Type': 'application/json'}

        if self.swagger_ui_path:
            @bp.route(self.swagger_ui_path)
            def swagger():
                return render_template('apiflask/swagger_ui.html',
                                       title=self.title, version=self.version)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc():
                return render_template('apiflask/redoc.html',
                                       title=self.title, version=self.version)

        if self.apispec_path or self.swagger_ui_path or self.redoc_path:
            self.register_blueprint(bp)

        @self.errorhandler(HTTPException)
        def handle_http_error(error):
            return self.error_handler_callback(error.status_code,
                                               error.message,
                                               error.detail,
                                               error.headers)

        if self.handle_basic_errrors:
            @self.errorhandler(401)
            @self.errorhandler(403)
            @self.errorhandler(404)
            @self.errorhandler(405)
            @self.errorhandler(500)
            def handle_basic_errrors(error):
                return self.error_handler_callback(error.code, error.description)

    def dispatch_request(self):
        """Overwrite the default dispatch method to pass view arguments as positional
        arguments.
        """
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule = req.url_rule
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if (
            getattr(rule, "provide_automatic_options", False)
            and req.method == "OPTIONS"
        ):
            return self.make_default_options_response()
        # otherwise dispatch to the handler for that endpoint
        return self.view_functions[rule.endpoint](*req.view_args.values())

    @property
    def title(self):
        return self.config['OPENAPI_TITLE']

    @property
    def version(self):
        return self.config['OPENAPI_VERSION']

    @property
    def apispec_path(self):
        return self.config['OPENAPI_SPEC_PATH']

    @property
    def swagger_ui_path(self):
        return self.config['SWAGGER_UI_PATH']

    @property
    def redoc_path(self):
        return self.config['REDOC_PATH']

    @property
    def tags(self):
        return self.config['OPENAPI_TAGS']

    @property
    def handle_basic_errrors(self):
        return self.config['HANDLE_BASIC_ERRORS']

    def process_apispec(self, f):
        self.apispec_callback = f
        return f

    def error_handler(self, f):
        self.error_handler_callback = f
        return f

    def default_error_handler(self, status_code, message, detail=None, headers=None):
        if detail is None:
            detail = {}
        body = {'detail': detail, 'message': message, 'status_code': status_code}
        if headers is None:
            return body, status_code
        else:
            return body, status_code, headers

    def get(self, rule, **options):
        return self.route(rule, **options, methods=['GET'])

    def post(self, rule, **options):
        return self.route(rule, **options, methods=['POST'])

    def put(self, rule, **options):
        return self.route(rule, **options, methods=['PUT'])

    def patch(self, rule, **options):
        return self.route(rule, **options, methods=['PATCH'])

    def delete(self, rule, **options):
        return self.route(rule, **options, methods=['DELETE'])

    def head(self, rule, **options):
        return self.route(rule, **options, methods=['HEAD'])

    def options(self, rule, **options):
        return self.route(rule, **options, methods=['OPTIONS'])

    def trace(self, rule, **options):
        return self.route(rule, **options, methods=['TRACE'])

    @property
    def apispec(self):
        if self._apispec is None:
            self._apispec = self._generate_apispec().to_dict()
            if self.apispec_callback:
                self._apispec = self.apispec_callback(self._apispec)
        return self._apispec

    def _generate_apispec(self):
        def resolver(schema):
            name = schema.__class__.__name__
            if name.endswith("Schema"):
                name = name[:-6] or name
            if schema.many:
                name += 'List'
            elif schema.partial:
                name += 'Update'
            return name

        # info object
        info = {}
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
        tags = self.tags
        if tags is None:
            # auto-generate tags from blueprints
            blueprints = []
            for rule in self.url_map.iter_rules():
                view_func = self.view_functions[rule.endpoint]
                if hasattr(view_func, '_spec'):
                    if '.' in rule.endpoint:
                        blueprint = rule.endpoint.split('.', 1)[0]
                        if blueprint not in blueprints:
                            blueprints.append(blueprint)
            tags = []
            for name, blueprint in self.blueprints.items():
                if name not in blueprints:
                    continue
                module = sys.modules[blueprint.import_name]
                tag = {'name': name.title()}
                if module.__doc__:
                    tag['description'] = module.__doc__.strip()
                tags.append(tag)

        ma_plugin = MarshmallowPlugin(schema_name_resolver=resolver)
        spec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version='3.0.3',
            plugins=[ma_plugin],
            info=info,
            tags=tags,
        )

        # configure flask-marshmallow URL types
        ma_plugin.converter.field_mapping[fields.URLFor] = ('string', 'url')
        ma_plugin.converter.field_mapping[fields.AbsoluteURLFor] = \
            ('string', 'url')
        if sqla is not None:
            ma_plugin.converter.field_mapping[sqla.HyperlinkRelated] = \
                ('string', 'url')

        # security schemes
        auth_schemes = []
        auth_names = []
        for rule in self.url_map.iter_rules():
            view_func = self.view_functions[rule.endpoint]
            if hasattr(view_func, '_spec'):
                auth = view_func._spec.get('auth')
                if auth is not None and auth not in auth_schemes:
                    auth_schemes.append(auth)
                    if isinstance(auth, HTTPBasicAuth):
                        name = 'basic_auth'
                    elif isinstance(auth, HTTPTokenAuth):
                        name = 'api_key'
                    else:
                        raise RuntimeError('Uknown authentication scheme')
                    if name in auth_names:
                        v = 2
                        new_name = f'{name}_{v}'
                        while new_name in auth_names:
                            v += 1
                            new_name = f'{name}_{v}'
                        name = new_name
                    auth_names.append(name)
        security = {}
        security_schemes = {}
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
            if auth.__doc__:
                security_schemes[name]['description'] = auth.__doc__.strip()
            elif auth.__class__.__doc__:
                security_schemes[name]['description'] = \
                    auth.__class__.__doc__.strip()
        for name, scheme in security_schemes.items():
            spec.components.security_scheme(name, scheme)

        # paths
        paths = {}
        rules = list(self.url_map.iter_rules())
        rules = sorted(rules, key=lambda rule: len(rule.rule))
        for rule in rules:
            operations = {}
            view_func = self.view_functions[rule.endpoint]
            if rule.endpoint.startswith('apiflask') or \
               rule.endpoint.startswith('static'):
                continue
            if not hasattr(view_func, '_spec'):
                view_func._spec = \
                    dict(_response=True, status_code=200, response_description=None)
            tag = None
            if '.' in rule.endpoint:
                tag = rule.endpoint.split('.', 1)[0].title()
            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if method not in rule.methods:
                    continue
                operation = {
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                        if location != 'body'
                    ],
                    'responses': {},
                }
                if tag:
                    operation['tags'] = [tag]

                if view_func._spec.get('summary'):
                    operation['summary'] = view_func._spec.get('summary')
                    operation['description'] = view_func._spec.get('description')
                else:
                    docs = (view_func.__doc__ or '').strip().split('\n')
                    if docs[0]:
                        operation['summary'] = docs[0]
                    else:
                        operation['summary'] = ' '.join(
                            view_func.__name__.split('_')).title()
                    if len(docs) > 1:
                        operation['description'] = '\n'.join(docs[1:]).strip()

                if view_func._spec.get('responses'):
                    for status_code, description in view_func._spec.get('responses').items():
                        operation['responses'][status_code] = {'description': description}

                if view_func._spec.get('response') or \
                   view_func._spec.get('_response'):
                    code = str(view_func._spec['status_code'])
                    schema = view_func._spec.get('response', {})
                    operation['responses'][code] = {
                        'content': {
                            'application/json': {
                                'schema': schema
                            }
                        }
                    }
                    operation['responses'][code]['description'] = \
                        view_func._spec['response_description'] or \
                        self.config['200_RESPONSE_DESCRIPTION']
                else:
                    operation['responses'] = {'204': {}}
                    operation['responses']['204']['description'] = \
                        self.config['204_RESPONSE_DESCRIPTION']

                if view_func._spec.get('body'):
                    operation['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': view_func._spec['body'],
                            }
                        }
                    }

                if view_func._spec.get('auth'):
                    operation['security'] = [{
                        security[view_func._spec['auth']]: view_func._spec[
                            'roles']
                    }]

                if view_func._spec.get('body') or view_func._spec.get('args'):
                    code = self.config['VALIDATION_ERROR_CODE']
                    operation['responses'][code] = {
                        'content': {
                            'application/json': {
                                'schema': validation_error_response_schema
                            }
                        }
                    }
                    operation['responses'][code]['description'] = \
                        self.config['VALIDATION_ERROR_DESCRIPTION']

                operations[method.lower()] = operation

            path_arguments = re.findall(r'<(([^:]+:)?([^>]+))>', rule.rule)
            if path_arguments:
                arguments = []
                for _, type, name in path_arguments:
                    arguments = {
                        'in': 'path',
                        'name': name,
                    }
                    if type == 'int:':
                        arguments['schema'] = {'type': 'integer'}
                    elif type == 'float:':
                        arguments['schema'] = {'type': 'number'}
                    else:
                        arguments['schema'] = {'type': 'string'}
                    for method, operation in operations.items():
                        operation['parameters'].insert(0, arguments)

            path = re.sub(r'<([^:]+:)?', '{', rule.rule).replace('>', '}')
            if path not in paths:
                paths[path] = operations
            else:
                paths[path].update(operations)
        for path, operations in paths.items():
            # sort by method before adding them to the spec
            sorted_operations = {}
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in operations:
                    sorted_operations[method] = operations[method]
            spec.path(path=path, operations=sorted_operations)

        return spec
