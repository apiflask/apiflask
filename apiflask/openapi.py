import re
import sys

from flask import Blueprint
from flask import render_template
from flask import current_app
from flask.config import ConfigAttribute
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


_REDOC_STANDALONE_JS = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/\
redoc.standalone.js'
_SWAGGER_UI_CSS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
_SWAGGER_UI_BUNDLE_JS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-bundle.js'
_SWAGGER_UI_STANDALONE_PRESET_JS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-standalone-preset.js'


class _OpenAPIMixin:
    #: The title of the API (openapi.info.title), defaults to "APIFlask".
    #: You can change it to the name of your API (e.g. "Pet API").
    title = None

    #: The version of the API (openapi.info.version), defaults to "1.0.0".
    version = None

    #: The description of the API (openapi.info.description).
    #:
    #: This attribute can also be configured from the config with the
    #: ``DESCRIPTION`` configuration key. Defaults to ``None``.
    description = ConfigAttribute('DESCRIPTION')

    #: The tags of the OpenAPI spec documentation (openapi.tags), accepts a
    #: list of dicts.
    #: You can also pass a simple list contains the tag name::
    #:
    #:     app.tags = ['foo', 'bar', 'baz']
    #:
    #: A standard OpenAPI tags list will look like this::
    #:
    #:     app.tags = [
    #:         {'name': 'foo', 'description': 'The description of foo'},
    #:         {'name': 'bar', 'description': 'The description of bar'},
    #:         {'name': 'baz', 'description': 'The description of baz'}
    #:     ]
    #:
    #: If not set, the blueprint names will be used as tags.
    #:
    #: This attribute can also be configured from the config with the
    #: ``TAGS`` configuration key. Defaults to ``None``.
    tags = ConfigAttribute('TAGS')

    #: The contact information of the API (openapi.info.contact).
    #: Example value:
    #:
    #:    app.contact = {
    #:        'name': 'API Support',
    #:        'url': 'http://www.example.com/support',
    #:        'email': 'support@example.com'
    #:    }
    #:
    #: This attribute can also be configured from the config with the
    #: ``CONTACT`` configuration key. Defaults to ``None``.
    contact = ConfigAttribute('CONTACT')

    #: The license of the API (openapi.info.license).
    #: Example value:
    #:
    #:    app.license = {
    #:        'name': 'Apache 2.0',
    #:        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    #:    }
    #:
    #: This attribute can also be configured from the config with the
    #: ``LICENSE`` configuration key. Defaults to ``None``.
    license = ConfigAttribute('LICENSE')

    #: The servers information of the API (openapi.servers), accepts multiple
    #: server dicts.
    #: Example value:
    #:
    #:    app.servers = [
    #:        {
    #:            'name': 'Production Server',
    #:            'url': 'http://api.example.com'
    #:        }
    #:    ]
    #:
    #: This attribute can also be configured from the config with the
    #: ``SERVERS`` configuration key. Defaults to ``None``.
    servers = ConfigAttribute('SERVERS')

    #: The external documentation information of the API (openapi.externalDocs).
    #: Example value:
    #:
    #:    app.external_docs = {
    #:       'description': 'Find more info here',
    #:       'url': 'http://docs.example.com'
    #:    }
    #:
    #: This attribute can also be configured from the config with the
    #: ``EXTERNAL_DOCS`` configuration key. Defaults to ``None``.
    external_docs = ConfigAttribute('EXTERNAL_DOCS')

    #: The terms of service URL of the API (openapi.info.termsOfService).
    #: Example value:
    #:
    #:    app.terms_of_service = "http://example.com/terms/"
    #:
    #: This attribute can also be configured from the config with the
    #: ``TERMS_OF_SERVICE`` configuration key. Defaults to ``None``.
    terms_of_service = ConfigAttribute('TERMS_OF_SERVICE')

    def __init__(self, title, version, spec_path, docs_path, redoc_path):
        self.title = title
        self.version = version
        self.spec_path = spec_path
        self.docs_path = docs_path
        self.redoc_path = redoc_path

    def _register_openapi_blueprint(self):
        bp = Blueprint(
            'openapi',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/apiflask'
        )

        if self.spec_path:
            @bp.route(self.spec_path)
            def spec():
                if self.spec_path.endswith('.yaml') or \
                   self.spec_path.endswith('.yml'):
                    # YAML spec
                    return self.apispec.to_yaml(), 200, \
                        {'Content-Type': 'text/vnd.yaml'}
                else:
                    # JSON spec
                    return self.apispec.to_dict()

        if self.docs_path:
            @bp.route(self.docs_path)
            def swagger_ui():
                return render_template('apiflask/swagger_ui.html',
                                       title=self.title, version=self.version)

            @bp.route(self.docs_path + '/oauth2-redirect')
            def swagger_ui_oauth_redirect():
                return render_template('apiflask/swagger_ui_oauth2_redirect.html',
                                       title=self.title, version=self.version)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc():
                return render_template('apiflask/redoc.html',
                                       title=self.title, version=self.version)

        if self.spec_path or self.docs_path or self.redoc_path:
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
        else:
            # Convert simple tags list into standard OpenAPI tags
            if isinstance(tags[0], str):
                for index, tag in enumerate(tags):
                    tags[index] = {'name': tag}

        # additional fields
        kwargs = {}
        if self.servers:
            kwargs['servers'] = self.servers
        if self.external_docs:
            kwargs['externalDocs'] = self.external_docs

        ma_plugin = MarshmallowPlugin(schema_name_resolver=resolver)
        spec = APISpec(
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
            # skip endpoints from openapi blueprint and the built-in static endpoint
            if rule.endpoint.startswith('openapi') or \
               rule.endpoint.startswith('static'):
                continue
            # skip endpoints from blueprints in config DOCS_HIDE_BLUEPRINTS list
            if '.' in rule.endpoint:
                blueprint_name = rule.endpoint.split('.', 1)[0]
                if blueprint_name in current_app.config['DOCS_HIDE_BLUEPRINTS']:
                    continue
            # register a default 200 response for bare views
            if self.config['AUTO_200_RESPONSE']:
                if not hasattr(view_func, '_spec'):
                    view_func._spec = \
                        dict(_response=True, status_code=200, response_description=None)

            # tag
            tag = None
            if view_func._spec.get('tag'):
                tag = view_func._spec.get('tag')
            else:
                # if tag not set, try to use blueprint name as tag
                if '.' in rule.endpoint:
                    tag = rule.endpoint.split('.', 1)[0].title()

            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if view_func._spec.get('hide'):
                    continue
                if method not in rule.methods:
                    continue
                operation = {
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                        if location == 'query'
                    ],
                    'responses': {},
                }
                if tag:
                    operation['tags'] = [tag]

                # summary and description
                if view_func._spec.get('summary'):
                    operation['summary'] = view_func._spec.get('summary')
                    operation['description'] = view_func._spec.get('description')
                else:
                    # auto-generate summary and description from dotstring
                    docs = (view_func.__doc__ or '').strip().split('\n')
                    if docs[0]:
                        # Use the first line of docstring as summary
                        operation['summary'] = docs[0]
                    else:
                        # Use the function name as summary
                        operation['summary'] = ' '.join(
                            view_func.__name__.split('_')).title()
                    if len(docs) > 1:
                        # Use the remain lines of docstring as description
                        operation['description'] = '\n'.join(docs[1:]).strip()

                # deprecated
                if view_func._spec.get('deprecated'):
                    operation['deprecated'] = view_func._spec.get('deprecated')

                # responses
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
                    if self.config['AUTO_204_RESPONSE']:
                        operation['responses'] = {'204': {}}
                        operation['responses']['204']['description'] = \
                            self.config['204_DESCRIPTION']

                # requestBody
                if view_func._spec.get('body'):
                    operation['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': view_func._spec['body'],
                            }
                        }
                    }

                # security
                if view_func._spec.get('auth'):
                    operation['security'] = [{
                        security[view_func._spec['auth']]: view_func._spec[
                            'roles']
                    }]

                # Add validation error response
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

            # parameters
            path_arguments = re.findall(r'<(([^<:]+:)?([^>]+))>', rule.rule)
            if path_arguments:
                arguments = []
                for _, type, name in path_arguments:
                    argument = {
                        'in': 'path',
                        'name': name,
                    }
                    if type == 'int:':
                        argument['schema'] = {'type': 'integer'}
                    elif type == 'float:':
                        argument['schema'] = {'type': 'number'}
                    else:
                        argument['schema'] = {'type': 'string'}
                    arguments.append(argument)

                for method, operation in operations.items():
                    operation['parameters'] = arguments + operation['parameters']

            path = re.sub(r'<([^<:]+:)?', '{', rule.rule).replace('>', '}')
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
