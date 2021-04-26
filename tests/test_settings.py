import pytest
from openapi_spec_validator import validate_spec
from flask.views import MethodView

from apiflask import APIFlask
from apiflask import APIBlueprint
from apiflask import input
from apiflask import output
from apiflask import auth_required
from apiflask import doc
from apiflask.schemas import EmptySchema
from apiflask.schemas import http_error_schema
from apiflask.security import HTTPBasicAuth

from .schemas import QuerySchema
from .schemas import FooSchema
from .schemas import ValidationErrorSchema
from .schemas import HTTPErrorSchema


def test_openapi_fields(app, client):
    openapi_version = '3.0.2'
    description = 'My API'
    tags = [
        {
            'name': 'foo',
            'description': 'some description for foo',
            'externalDocs': {
                'description': 'Find more info about foo here',
                'url': 'https://docs.example.com/'
            }
        },
        {'name': 'bar', 'description': 'some description for bar'},
    ]
    contact = {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    }
    license = {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
    terms_of_service = 'http://example.com/terms/'
    external_docs = {
        'description': 'Find more info here',
        'url': 'https://docs.example.com/'
    }
    servers = [
        {
            'url': 'http://localhost:5000/',
            'description': 'Development server'
        },
        {
            'url': 'https://api.example.com/',
            'description': 'Production server'
        }
    ]
    app.config['OPENAPI_VERSION'] = openapi_version
    app.config['DESCRIPTION'] = description
    app.config['TAGS'] = tags
    app.config['CONTACT'] = contact
    app.config['LICENSE'] = license
    app.config['TERMS_OF_SERVICE'] = terms_of_service
    app.config['EXTERNAL_DOCS'] = external_docs
    app.config['SERVERS'] = servers

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['openapi'] == openapi_version
    assert rv.json['tags'] == tags
    assert rv.json['servers'] == servers
    assert rv.json['externalDocs'] == external_docs
    assert rv.json['info']['description'] == description
    assert rv.json['info']['contact'] == contact
    assert rv.json['info']['license'] == license
    assert rv.json['info']['termsOfService'] == terms_of_service


def test_json_spec_mimetype(app, client):
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/json'

    app.config['JSON_SPEC_MIMETYPE'] = 'application/custom.json'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/custom.json'


def test_yaml_spec_mimetype():
    app = APIFlask(__name__, spec_path='/openapi.yaml')
    client = app.test_client()

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/vnd.yaml'

    app.config['YAML_SPEC_MIMETYPE'] = 'text/custom.yaml'

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/custom.yaml'


def test_auto_tags(app, client):
    bp = APIBlueprint('foo', __name__)
    app.config['AUTO_TAGS'] = False

    @bp.get('/')
    def foo():
        pass

    app.register_blueprint(bp)
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == []
    assert 'tags' not in rv.json['paths']['/']['get']


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_path_summary(app, client, config_value):
    app.config['AUTO_PATH_SUMMARY'] = config_value

    @app.get('/foo')
    def foo():
        pass

    @app.get('/bar')
    def get_bar():
        pass

    @app.get('/baz')
    def get_baz():
        """Baz Summary"""
        pass

    @app.get('/spam')
    def get_spam():
        """Spam Summary

        some description
        """
        pass

    @app.get('/eggs')
    @doc(summary='Eggs from doc decortor')
    def get_eggs():
        """Eggs Summary

        some description
        """
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert rv.json['paths']['/foo']['get']['summary'] == 'Foo'
        assert rv.json['paths']['/bar']['get']['summary'] == 'Get Bar'
        assert rv.json['paths']['/baz']['get']['summary'] == 'Baz Summary'
        assert rv.json['paths']['/spam']['get']['summary'] == 'Spam Summary'
    else:
        assert 'summary' not in rv.json['paths']['/foo']['get']
        assert 'summary' not in rv.json['paths']['/bar']['get']
        assert 'summary' not in rv.json['paths']['/baz']['get']
        assert 'summary' not in rv.json['paths']['/spam']['get']
    assert rv.json['paths']['/eggs']['get']['summary'] == 'Eggs from doc decortor'


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_path_summary_with_methodview(app, client, config_value):
    app.config['AUTO_PATH_SUMMARY'] = config_value

    @app.route('/foo')
    class Foo(MethodView):
        def get(self):
            pass

        def post(self):
            """Post Summary"""
            pass

        def delete(self):
            """Delete Summary

            some description
            """
            pass

        @doc(summary='Put from doc decortor')
        def put(self):
            """Delete Summary

            some description
            """
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert rv.json['paths']['/foo']['get']['summary'] == 'Get Foo'
        assert rv.json['paths']['/foo']['post']['summary'] == 'Post Summary'
        assert rv.json['paths']['/foo']['delete']['summary'] == 'Delete Summary'
    else:
        assert 'summary' not in rv.json['paths']['/foo']['get']
        assert 'summary' not in rv.json['paths']['/foo']['post']
        assert 'summary' not in rv.json['paths']['/foo']['delete']
    assert rv.json['paths']['/foo']['put']['summary'] == 'Put from doc decortor'


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_path_description(app, client, config_value):
    app.config['AUTO_PATH_DESCRIPTION'] = config_value

    @app.get('/foo')
    def get_foo():
        """Foo

        some description for foo
        """
        pass

    @app.get('/bar')
    @doc(description='bar from doc decortor')
    def get_bar():
        """Bar

        some description for bar
        """
        pass

    @app.route('/baz')
    class Baz(MethodView):
        def get(self):
            """Baz

            some description for baz
            """
            pass

        @doc(description='post from doc decortor')
        def post(self):
            """Baz

            some description for baz
            """
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert rv.json['paths']['/foo']['get']['description'] == 'some description for foo'
        assert rv.json['paths']['/baz']['get']['description'] == 'some description for baz'
    else:
        assert 'description' not in rv.json['paths']['/foo']['get']
        assert 'description' not in rv.json['paths']['/baz']['get']
    assert rv.json['paths']['/bar']['get']['description'] == 'bar from doc decortor'
    assert rv.json['paths']['/baz']['post']['description'] == 'post from doc decortor'


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_200_response_for_bare_views(app, client, config_value):
    app.config['AUTO_200_RESPONSE'] = config_value

    @app.get('/foo')
    def foo():
        pass

    @app.route('/bar')
    class Bar(MethodView):
        def get(self):
            pass

        def post(self):
            pass

    @app.route('/baz')
    class Baz(MethodView):
        def get(self):
            pass

        @input(FooSchema)
        def post(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert bool('/foo' in rv.json['paths']) is config_value
    assert bool('/bar' in rv.json['paths']) is config_value
    assert '/baz' in rv.json['paths']
    assert bool('get' in rv.json['paths']['/baz']) is config_value
    assert 'post' in rv.json['paths']['/baz']


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_200_response_for_no_output_views(app, client, config_value):
    app.config['AUTO_200_RESPONSE'] = config_value

    @app.get('/foo')
    @input(QuerySchema, 'query')
    def foo():
        pass

    @app.route('/bar')
    class Bar(MethodView):
        @input(QuerySchema, 'query')
        def get(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/foo' in rv.json['paths']
    assert '/bar' in rv.json['paths']
    assert bool('200' in rv.json['paths']['/foo']['get']['responses']) is config_value
    assert bool('200' in rv.json['paths']['/bar']['get']['responses']) is config_value


def test_response_description_config(app, client):
    app.config['SUCCESS_DESCRIPTION'] = 'Success'

    @app.get('/foo')
    @input(FooSchema)  # 200
    def only_body_schema(foo):
        pass

    @app.get('/bar')
    @output(FooSchema, 201)
    def create():
        pass

    @app.get('/baz')
    @output(EmptySchema)  # 204
    def no_schema():
        pass

    @app.get('/spam')
    @output(FooSchema, 206)
    def spam():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses'][
        '200']['description'] == 'Success'
    assert rv.json['paths']['/bar']['get']['responses'][
        '201']['description'] == 'Success'
    assert rv.json['paths']['/baz']['get']['responses'][
        '204']['description'] == 'Success'
    assert rv.json['paths']['/spam']['get']['responses'][
        '206']['description'] == 'Success'


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_validation_error_response(app, client, config_value):
    app.config['AUTO_VALIDATION_ERROR_RESPONSE'] = config_value

    @app.post('/foo')
    @input(FooSchema)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert bool('400' in rv.json['paths']['/foo']['post']['responses']) is config_value
    if config_value:
        assert 'ValidationError' in rv.json['components']['schemas']
        assert '#/components/schemas/ValidationError' in \
            rv.json['paths']['/foo']['post']['responses']['400'][
                'content']['application/json']['schema']['$ref']


def test_validation_error_status_code_and_description(app, client):
    app.config['VALIDATION_ERROR_STATUS_CODE'] = 422
    app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Bad'

    @app.post('/foo')
    @input(FooSchema)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['422'] is not None
    assert rv.json['paths']['/foo']['post']['responses'][
        '422']['description'] == 'Bad'


@pytest.mark.parametrize('schema', [
    http_error_schema,
    ValidationErrorSchema
])
def test_validation_error_schema(app, client, schema):
    app.config['VALIDATION_ERROR_SCHEMA'] = schema

    @app.post('/foo')
    @input(FooSchema)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['400']
    assert rv.json['paths']['/foo']['post']['responses']['400'][
        'description'] == 'Validation error'
    assert 'ValidationError' in rv.json['components']['schemas']


def test_validation_error_schema_bad_type(app):
    app.config['VALIDATION_ERROR_SCHEMA'] = 'schema'

    @app.post('/foo')
    @input(FooSchema)
    def foo():
        pass

    with pytest.raises(RuntimeError):
        app.spec


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_auth_error_response(app, client, config_value):
    app.config['AUTO_AUTH_ERROR_RESPONSE'] = config_value
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert bool('401' in rv.json['paths']['/foo']['post']['responses']) is config_value
    if config_value:
        assert 'HTTPError' in rv.json['components']['schemas']
        assert '#/components/schemas/HTTPError' in \
            rv.json['paths']['/foo']['post']['responses']['401'][
                'content']['application/json']['schema']['$ref']


def test_auth_error_status_code_and_description(app, client):
    app.config['AUTH_ERROR_STATUS_CODE'] = 403
    app.config['AUTH_ERROR_DESCRIPTION'] = 'Bad'
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['403'] is not None
    assert rv.json['paths']['/foo']['post']['responses'][
        '403']['description'] == 'Bad'


def test_auth_error_schema(app, client):
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['401']
    assert 'HTTPError' in rv.json['components']['schemas']


def test_http_auth_error_response(app, client):
    @app.get('/foo')
    @output(FooSchema)
    @doc(responses={204: 'empty', 400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'HTTPError' in rv.json['components']['schemas']
    assert '#/components/schemas/HTTPError' in \
        rv.json['paths']['/foo']['get']['responses']['404'][
            'content']['application/json']['schema']['$ref']
    assert '#/components/schemas/HTTPError' in \
        rv.json['paths']['/foo']['get']['responses']['500'][
            'content']['application/json']['schema']['$ref']
    assert 'content' not in rv.json['paths']['/foo']['get']['responses']['204']


@pytest.mark.parametrize('schema', [
    http_error_schema,
    HTTPErrorSchema
])
def test_http_error_schema(app, client, schema):
    app.config['HTTP_ERROR_SCHEMA'] = schema

    @app.get('/foo')
    @output(FooSchema)
    @doc(responses={400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['404']
    assert 'HTTPError' in rv.json['components']['schemas']


def test_http_error_schema_bad_type(app):
    app.config['HTTP_ERROR_SCHEMA'] = 'schema'

    @app.get('/foo')
    @output(FooSchema)
    @doc(responses={400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    with pytest.raises(RuntimeError):
        app.spec


def test_docs_favicon(app, client):
    app.config['DOCS_FAVICON'] = '/my-favicon.png'

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'href="/my-favicon.png"' in rv.data


@pytest.mark.parametrize('config_value', [True, False])
def test_docs_use_google_font(app, client, config_value):
    app.config['REDOC_USE_GOOGLE_FONT'] = config_value

    rv = client.get('/redoc')
    assert rv.status_code == 200
    assert bool(b'fonts.googleapis.com' in rv.data) is config_value


def test_redoc_standalone_js(app, client):
    app.config['REDOC_STANDALONE_JS'] = 'https://cdn.example.com/redoc.js'

    rv = client.get('/redoc')
    assert rv.status_code == 200
    assert b'src="https://cdn.example.com/redoc.js"' in rv.data


def test_swagger_ui_resources(app, client):
    app.config['SWAGGER_UI_CSS'] = 'https://cdn.example.com/swagger-ui.css'
    app.config['SWAGGER_UI_BUNDLE_JS'] = 'https://cdn.example.com/swagger-ui.bundle.js'
    app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = \
        'https://cdn.example.com/swagger-ui.preset.js'

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'href="https://cdn.example.com/swagger-ui.css"' in rv.data
    assert b'src="https://cdn.example.com/swagger-ui.bundle.js"' in rv.data
    assert b'src="https://cdn.example.com/swagger-ui.preset.js"' in rv.data


def test_swagger_ui_layout(app, client):
    app.config['SWAGGER_UI_LAYOUT'] = 'StandaloneLayout'

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'StandaloneLayout' in rv.data
    assert b'BaseLayout' not in rv.data


def test_swagger_ui_config(app, client):
    app.config['SWAGGER_UI_CONFIG'] = {
        'deepLinking': False,
        'layout': 'StandaloneLayout'
    }

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'"deepLinking": false' in rv.data
    assert b'"layout": "StandaloneLayout"' in rv.data


def test_swagger_ui_oauth_config(app, client):
    app.config['SWAGGER_UI_OAUTH_CONFIG'] = {
        'clientId': 'foo',
        'usePkceWithAuthorizationCodeGrant': True
    }

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'ui.initOAuth(' in rv.data
    assert b'"clientId": "foo"' in rv.data
    assert b'"usePkceWithAuthorizationCodeGrant": true' in rv.data
