import re
import sys
from json import dumps

from flask import Blueprint
from flask import render_template
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_marshmallow import fields
try:
    from flask_marshmallow import sqla
except ImportError:
    sqla = None
try:
    from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
except ImportError:  # pragma: no cover
    HTTPBasicAuth = None
    HTTPTokenAuth = None

from .schemas import validation_error_response_schema


class _OpenAPIMixin:
    #: The title of the API, defaults to "APIFlask".
    #: You can change it to the name of your API (e.g. "Pet API").
    title = None
    #: The version of the API, defaults to "1.0.0".
    version = None
    #: The tags of the OpenAPI spec documentation, accept a list as value.
    # TODO add usage example
    tags = None

    def __init__(self, title, version, tags, spec_path, swagger_path, redoc_path):
        self.title = title
        self.version = version
        self.tags = tags
        self.spec_path = spec_path
        self.swagger_path = swagger_path
        self.redoc_path = redoc_path

    def register_openapi_blueprint(self):
        bp = Blueprint('openapi', __name__, template_folder='templates')

        if self.spec_path:
            @bp.route(self.spec_path)
            def spec():
                if self.spec_path.endswith('.yaml') or \
                   self.spec_path.endswith('.yml'):
                    return self.apispec.to_yaml(), 200, \
                        {'Content-Type': 'text/vnd.yaml'}

                else:
                    return dumps(self.apispec.to_dict()), 200, \
                        {'Content-Type': 'application/json'}

        if self.swagger_path:
            @bp.route(self.swagger_path)
            def swagger_ui():
                return render_template('apiflask/swagger_ui.html',
                                       title=self.title, version=self.version)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc():
                return render_template('apiflask/redoc.html',
                                       title=self.title, version=self.version)

        if self.spec_path or self.swagger_path or self.redoc_path:
            self.register_blueprint(bp)

    def process_apispec(self, f):
        self.apispec_callback = f
        return f

    @property
    def apispec(self):
        if self._apispec is None:
            self._apispec = self._generate_apispec()
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
            if rule.endpoint.startswith('openapi') or \
               rule.endpoint.startswith('static'):
                continue
            if not hasattr(view_func, '_spec'):
                view_func._spec = \
                    dict(_response=True, status_code=200, response_description=None)

            tag = None
            if view_func._spec.get('tag'):
                tag = view_func._spec.get('tag')

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
                        self.config['200_DESCRIPTION']
                else:
                    operation['responses'] = {'204': {}}
                    operation['responses']['204']['description'] = \
                        self.config['204_DESCRIPTION']

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
