from flask import Flask
from flask.globals import _request_ctx_stack
from flask.config import ConfigAttribute
from werkzeug.datastructures import ImmutableDict

from .openapi import _OpenAPIMixin
from .exceptions import HTTPException


class APIFlask(Flask, _OpenAPIMixin):

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

        self.register_openapi_blueprint()

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

    # properties forwarding to built-in config variables
    openapi_title = ConfigAttribute('OPENAPI_TITLE')
    openapi_version = ConfigAttribute('OPENAPI_VERSION')
    openapi_spec_path = ConfigAttribute('OPENAPI_SPEC_PATH')
    swagger_ui_path = ConfigAttribute('SWAGGER_UI_PATH')
    redoc_path = ConfigAttribute('REDOC_PATH')
    openapi_tags = ConfigAttribute('OPENAPI_TAGS')
    handle_basic_errrors = ConfigAttribute('HANDLE_BASIC_ERRORS')

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

    # shortcuts for app.route
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
