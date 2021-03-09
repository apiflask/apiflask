from flask import Flask
from flask.globals import _request_ctx_stack
from werkzeug.datastructures import ImmutableDict

from .openapi import _OpenAPIMixin
from .exceptions import HTTPException


class APIFlask(Flask, _OpenAPIMixin):
    """
    The Flask object with some Web API support.

    :param import_name: the name of the application package.
    :param title: The title of the API, defaults to "APIFlask".
        You can change it to the name of your API (e.g. "Pet API").
    :param version: The version of the API, defaults to "1.0.0".
    :param tags: The tags of the OpenAPI spec documentation, accept a list as value.
    :param spec_path: The path to OpenAPI Spec documentation. It
        defaults to ``/openapi.json```, if the path end with ``.yaml``
        or ``.yml``, the YAML format of the OAS will be returned.
    :param swagger_path: The path to Swagger UI documentation.
    :param redoc_path: The path to Redoc documentation.
    :param handle_errors: If True, APIFlask will return a JSON response
        for basic errors including 401, 403, 404, 405, 500.
    """
    #:  Default configuration variables.
    api_default_config = ImmutableDict(
        {
            '200_DESCRIPTION': 'Successful response',
            '204_DESCRIPTION': 'Empty response',
            'VALIDATION_ERROR_CODE': 400,
            'VALIDATION_ERROR_DESCRIPTION': 'Validation error',
        }
    )

    def __init__(
        self,
        import_name,
        title='APIFlask',
        version='1.0.0',
        tags=None,
        spec_path='/openapi.json',
        swagger_path='/docs',
        redoc_path='/redoc',
        handle_basic_errors=True,
        **kwargs
    ):
        super(APIFlask, self).__init__(import_name, **kwargs)
        _OpenAPIMixin.__init__(
            self,
            title=title,
            version=version,
            tags=tags,
            spec_path=spec_path,
            swagger_path=swagger_path,
            redoc_path=redoc_path
        )

        # Set default config
        self.config.update(self.api_default_config)

        self.handle_basic_errors = handle_basic_errors

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

        if self.handle_basic_errors:
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
