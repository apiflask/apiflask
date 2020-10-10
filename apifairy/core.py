from json import dumps
import re
import sys

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import current_app, Blueprint, render_template
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

from apifairy.exceptions import ValidationError


class APIFairy:
    def __init__(self, app=None):
        self.title = None
        self.version = None
        self.apispec_path = None
        self.ui = None
        self.ui_path = None
        self.tags = None

        self.apispec_callback = None
        self.error_handler_callback = self.default_error_handler
        self._apispec = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.title = app.config.get('APIFAIRY_TITLE', 'No title')
        self.version = app.config.get('APIFAIRY_VERSION', 'No version')
        self.apispec_path = app.config.get('APIFAIRY_APISPEC_PATH',
                                           '/apispec.json')
        self.ui = app.config.get('APIFAIRY_UI', 'redoc')
        self.ui_path = app.config.get('APIFAIRY_UI_PATH', '/docs')
        self.tags = app.config.get('APIFAIRY_TAGS')

        bp = Blueprint('apifairy', __name__, template_folder='templates')

        if self.apispec_path:
            @bp.route(self.apispec_path)
            def json():
                return dumps(self.apispec), 200, \
                    {'Content-Type': 'application/json'}

        if self.ui_path:
            @bp.route(self.ui_path)
            def docs():
                return render_template(f'apifairy/{self.ui}.html',
                                       title=self.title, version=self.version)

        if self.apispec_path or self.ui_path:
            app.register_blueprint(bp)

        @app.errorhandler(ValidationError)
        def http_error(error):
            return self.error_handler_callback(error.status_code,
                                               error.messages)

    def process_apispec(self, f):
        self.apispec_callback = f
        return f

    def error_handler(self, f):
        self.error_handler_callback = f
        return f

    def default_error_handler(self, status_code, messages):
        return {'messages': messages}, status_code

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
        module_name = current_app.import_name
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
            for rule in current_app.url_map.iter_rules():
                view_func = current_app.view_functions[rule.endpoint]
                if hasattr(view_func, '_spec'):
                    if '.' in rule.endpoint:
                        blueprint = rule.endpoint.split('.', 1)[0]
                        if blueprint not in blueprints:
                            blueprints.append(blueprint)
            tags = []
            for name, blueprint in current_app.blueprints.items():
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
        for rule in current_app.url_map.iter_rules():
            view_func = current_app.view_functions[rule.endpoint]
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
        rules = list(current_app.url_map.iter_rules())
        rules = sorted(rules, key=lambda rule: len(rule.rule))
        for rule in rules:
            operations = {}
            view_func = current_app.view_functions[rule.endpoint]
            if not hasattr(view_func, '_spec'):
                continue
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
                }
                if tag:
                    operation['tags'] = [tag]
                docs = (view_func.__doc__ or '').strip().split('\n')
                if docs:
                    operation['summary'] = docs[0]
                if len(docs) > 1:
                    operation['description'] = '\n'.join(docs[1:]).strip()
                if view_func._spec.get('response'):
                    code = str(view_func._spec['status_code'])
                    operation['responses'] = {
                        code: {
                            'content': {
                                'application/json': {
                                    'schema': view_func._spec.get('response')
                                }
                            }
                        }
                    }
                    operation['responses'][code]['description'] = \
                        view_func._spec['description'] or ''
                else:
                    operation['responses'] = {'204': {}}

                if view_func._spec.get('other_responses'):
                    for status_code, description in view_func._spec.get(
                            'other_responses').items():
                        operation['responses'][status_code] = \
                            {'description': description}

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
