import re
import sys

from flask import Blueprint
from flask import render_template
from flask.config import ConfigAttribute
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_marshmallow import fields
try:
    from flask_marshmallow import sqla
except ImportError:
    sqla = None

from .security import HTTPBasicAuth, HTTPTokenAuth
from .schemas import validation_error_response_schema


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

    def __init__(
        self,
        title,
        version,
        spec_path,
        docs_path,
        redoc_path,
        docs_oauth2_redirect_path,
        enable_openapi
    ):
        self.title = title
        self.version = version
        self.spec_path = spec_path
        self.docs_path = docs_path
        self.redoc_path = redoc_path
        self.docs_oauth2_redirect_path = docs_oauth2_redirect_path
        self.enable_openapi = enable_openapi

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
                    return self.get_spec('yaml'), 200, \
                        {'Content-Type': 'text/vnd.yaml'}
                else:
                    # JSON spec
                    return self.get_spec('json')

        if self.docs_path:
            @bp.route(self.docs_path)
            def swagger_ui():
                return render_template('apiflask/swagger_ui.html',
                                       title=self.title, version=self.version)

            if self.docs_oauth2_redirect_path:
                @bp.route(self.docs_oauth2_redirect_path)
                def swagger_ui_oauth_redirect():
                    return render_template('apiflask/swagger_ui_oauth2_redirect.html',
                                           title=self.title, version=self.version)

        if self.redoc_path:
            @bp.route(self.redoc_path)
            def redoc():
                return render_template('apiflask/redoc.html',
                                       title=self.title, version=self.version)

        if self.enable_openapi and (
            self.spec_path or self.docs_path or self.redoc_path
        ):
            self.register_blueprint(bp)

    def get_spec(self, spec_format=None):
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

    def spec_processor(self, f):
        self.spec_callback = f
        return f

    @property
    def spec(self):
        return self.get_spec()

    def _generate_spec(self):
        def resolver(schema):
            name = schema.__class__.__name__
            if name.endswith('Schema'):
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
        tags = self.tags
        if tags is not None:
            # Convert simple tags list into standard OpenAPI tags
            if isinstance(tags[0], str):
                for index, tag in enumerate(tags):
                    tags[index] = {'name': tag}
        else:
            tags = []
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
                    tags.append(tag)

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
        if sqla is not None:  # pragma: no cover
            ma_plugin.converter.field_mapping[sqla.HyperlinkRelated] = \
                ('string', 'url')

        # security schemes
        auth_schemes = []
        auth_names = []
        auth_blueprints = {}

        def update_auth_schemas_names(auth):
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
                    auth = f._spec.get('auth')
                    if auth is not None and auth not in auth_schemes:
                        auth_blueprints[blueprint_name] = {
                            'auth': auth,
                            'roles': f._spec.get('roles')
                        }
                        update_auth_schemas_names(auth)

        for rule in self.url_map.iter_rules():
            view_func = self.view_functions[rule.endpoint]
            if hasattr(view_func, '_spec'):
                auth = view_func._spec.get('auth')
                if auth is not None and auth not in auth_schemes:
                    update_auth_schemas_names(auth)

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

            if hasattr(auth, 'description') and auth.description is not None:
                security_schemes[name]['description'] = auth.description

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
                if blueprint_name in self.config['DOCS_HIDE_BLUEPRINTS']:
                    continue
            else:
                blueprint_name = None
            # register a default 200 response for bare views
            if not hasattr(view_func, '_spec'):
                if self.config['AUTO_200_RESPONSE']:
                    view_func._spec = {
                        '_response': True,
                        'status_code': 200,
                        'response_description': None
                    }
                else:
                    continue  # pragma: no cover
            # skip views flagged with @doc(hide=True)
            if view_func._spec.get('hide'):
                continue

            # tag
            tags = None
            if view_func._spec.get('tags'):
                tags = view_func._spec.get('tags')
            else:
                # if tag not set, try to use blueprint name as tag
                if self.tags is None and self.config['AUTO_TAGS']:
                    if blueprint_name is not None:
                        blueprint = self.blueprints[blueprint_name]
                        if hasattr(blueprint, 'tag') and blueprint.tag is not None:
                            if isinstance(blueprint.tag, dict):
                                tags = blueprint.tag['name']
                            else:
                                tags = blueprint.tag
                        else:
                            tags = blueprint_name.title()

            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if method not in rule.methods:
                    continue
                operation = {
                    'parameters': [
                        {'in': location, 'schema': schema}
                        for schema, location in view_func._spec.get('args', [])
                    ],
                    'responses': {},
                }
                if tags:
                    if isinstance(tags, list):
                        operation['tags'] = tags
                    else:
                        operation['tags'] = [tags]

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
                descriptions = {
                    '200': self.config['DEFAULT_200_DESCRIPTION'],
                    '204': self.config['DEFAULT_204_DESCRIPTION'],
                }

                def update_responses(status_code, schema, description):
                    operation['responses'][status_code] = {
                        'content': {
                            'application/json': {
                                'schema': schema
                            }
                        }
                    }
                    operation['responses'][status_code]['description'] = description

                if view_func._spec.get('response') or view_func._spec.get('_response'):
                    status_code = str(view_func._spec['status_code'])
                    schema = view_func._spec.get('response', {})
                    description = view_func._spec['response_description'] \
                        or descriptions[status_code]
                    update_responses(status_code, schema, description)
                else:
                    # add a default 200 response for views without using @output
                    # or @doc(responses={...})
                    if view_func._spec.get('responses') is None and \
                       self.config['AUTO_200_RESPONSE']:
                        update_responses('200', {}, descriptions['200'])

                # Add validation error response
                if view_func._spec.get('body') or view_func._spec.get('args'):
                    status_code = str(self.config['VALIDATION_ERROR_CODE'])
                    schema = validation_error_response_schema
                    description = self.config['VALIDATION_ERROR_DESCRIPTION']
                    update_responses(status_code, validation_error_response_schema, description)

                if view_func._spec.get('responses'):
                    for status_code, description in view_func._spec.get('responses').items():
                        status_code = str(status_code)
                        if status_code in operation['responses']:
                            operation['responses'][status_code]['description'] = description
                        else:
                            operation['responses'][status_code] = {'description': description}

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
