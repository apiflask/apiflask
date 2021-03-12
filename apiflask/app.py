from flask import Flask
from flask.globals import _request_ctx_stack
from werkzeug.datastructures import ImmutableDict
from werkzeug.exceptions import HTTPException as WerkzeugHTTPException

from .openapi import _OpenAPIMixin
from .exceptions import HTTPException


class APIFlask(Flask, _OpenAPIMixin):
    """
    The Flask object with some Web API support.

    :param import_name: the name of the application package.
    :param title: The title of the API, defaults to "APIFlask".
        You can change it to the name of your API (e.g. "Pet API").
    :param version: The version of the API, defaults to "1.0.0".
    :param tags: The tags of the OpenAPI spec documentation, accepts a list.
        See :attr:`tags` for more details.
    :param spec_path: The path to OpenAPI Spec documentation. It
        defaults to ``/openapi.json```, if the path end with ``.yaml``
        or ``.yml``, the YAML format of the OAS will be returned.
    :param swagger_path: The path to Swagger UI documentation.
    :param redoc_path: The path to Redoc documentation.
    :param json_errors: If True, APIFlask will return a JSON response
        for HTTP errors.
    """
    #:  Default configuration variables.
    api_default_config = ImmutableDict(
        {
            'DESCRIPTION': None,
            'TAGS': None,
            'CONTACT': None,
            'LICENSE': None,
            'SERVERS': None,
            'EXTERNAL_DOCS': None,
            'TERMS_OF_SERVICE': None,
            '200_DESCRIPTION': 'Successful response',
            '204_DESCRIPTION': 'Empty response',
            'VALIDATION_ERROR_CODE': 400,
            'VALIDATION_ERROR_DESCRIPTION': 'Validation error',
            'UNKNOWN_ERROR_MESSAGE': 'Unknown error',
            'DOCS_FAVICON': None,
            'DOCS_USE_GOOGLE_FONT': True,
            'REDOC_STANDALONE_JS': 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js',
            'SWAGGER_UI_CSS': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css',
            'SWAGGER_UI_BUNDLE_JS': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js',
            'SWAGGER_UI_STANDALONE_PRESET_JS': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
            'SWAGGER_UI_LAYOUT': 'BaseLayout',
            'SWAGGER_UI_OAUTH_CONFIG': None,
            'SWAGGER_UI_CONFIG': None,
        }
    )

    def __init__(
        self,
        import_name,
        title='APIFlask',
        version='0.1.0',
        spec_path='/openapi.json',
        docs_path='/docs',
        redoc_path='/redoc',
        json_errors=True,
        **kwargs
    ):
        super(APIFlask, self).__init__(import_name, **kwargs)
        _OpenAPIMixin.__init__(
            self,
            title=title,
            version=version,
            spec_path=spec_path,
            docs_path=docs_path,
            redoc_path=redoc_path
        )

        # Set default config
        self.config.update(self.api_default_config)

        self.json_errors = json_errors

        self.apispec_callback = None
        self.error_handler_func = self.default_error_handler
        self._apispec = None

        self._register_openapi_blueprint()

        @self.errorhandler(HTTPException)
        def handle_http_error(error):
            return self.error_handler_callback(error.status_code,
                                               error.message,
                                               error.detail,
                                               error.headers)

        if self.json_errors:
            @self.errorhandler(WerkzeugHTTPException)
            def handle_werkzeug_errrors(error):
                return self.error_handler_callback(error.code, error.description)

    def dispatch_request(self):
        """Overwrite the default dispatch method to pass view arguments as positional
        arguments. With this overwrite, the view function can accept the parameters in
        a intuitive way (from top to bottom, from left to right)::

            @app.get('/pets/<name>/<int:pet_id>/<age>')  # -> name, pet_id, age
            @input(QuerySchema)  # -> query
            @output(PetSchema)  # -> pet
            def get_pet(name, pet_id, age, query, pet):
                pass

        .. versionadded:: 0.2.0
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

    def errorhandler_callback(self, f):
        """Registers a error handler callback function.
        
        The callback function will be called when validation error hanppend when
        parse a request or an exception triggerd with exceptions.HTTPException or
        :func:`exceptions.abort`. It must accept four positional arguments (i.e.
        ``status_code, message, detail, headers``) and return a valid response::

            @app.errorhandler_callback
            def my_error_handler(status_code, message, detail, headers):
                return {
                    'status_code': status_code,
                    'message': message,
                    'detail': detail
                    }, status_code, headers

        The arguments are:
        - status_code: If the error triggerd by validation error, the value will be
            400 (default) or the value you passed in config ``VALIDATION_ERROR_CODE``.
            If the error triggerd by HTTP, it will be the status code you passed.
            Otherwise, it will be the status code set by Werkzueg when processing the request.
        - message: The error description for this error, either you passed or grab from Werkzeug.
        - detail: The detail of the error, it will be filled when validation error happaned, the
            structure will be::

                "<location>": {
                    "<field_name>": ["<error_message>", ...],
                    ...
                },
                ...

            The value of ``location`` can be ``json`` (i.e. request body) or ``query``
            (i.e. query string) depend on the palace the validation error happened.
        - headers: The value will be None unless you pass it in HTTPException or abort.

        If you want, you can rewrite the whole response body to anything you like::

            @app.errorhandler_callback
            def my_error_handler(status_code, message, detail, headers):
                return {'error_detail': detail}, status_code, headers

        However, I would recommend to keep the ``detail`` since it contains the detail
        information about the validation error.
        """
        self.error_handler_func = f
        return f

    def default_error_handler(self, status_code, message, detail=None, headers=None):
        if detail is None:
            detail = {}
        body = {'detail': detail, 'message': message, 'status_code': status_code}
        if headers is None:
            return body, status_code
        else:
            return body, status_code, headers

    # TODO Remove these shortcuts when pin Flask>=2.0
    def get(self, rule, **options):
        """Shortcut for ``app.route()``.
        
        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['GET'], **options)

    #: Shortcut method for app.route(methods=['POST']).
    def post(self, rule, **options):
        """Shortcut for ``app.route(methods=['POST'])``.
        
        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['POST'], **options)

    #: Shortcut method for app.route(methods=['PUT']).
    def put(self, rule, **options):
        """Shortcut for ``app.route(methods=['PUT'])``.
        
        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['PUT'], **options)

    def patch(self, rule, **options):
        """Shortcut for ``app.route(methods=['PATCH'])``.
        
        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['PATCH'], **options)

    def delete(self, rule, **options):
        """Shortcut for ``app.route(methods=['DELETE'])``.
        
        .. versionadded:: 0.2.0
        """
        return self.route(rule, methods=['DELETE'], **options)
