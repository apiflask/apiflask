from apiflask.decorators import auth_required
import pytest
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint, input, output, doc
from apiflask.schemas import EmptySchema, http_error_schema
from apiflask.security import HTTPBasicAuth

from .schemas import QuerySchema, FooSchema
from .schemas import ValidationErrorSchema, AuthorizationErrorSchema, HTTPErrorSchema


def test_openapi_fields(app, client):
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
    assert rv.json['tags'] == tags
    assert rv.json['servers'] == servers
    assert rv.json['externalDocs'] == external_docs
    assert rv.json['info']['description'] == description
    assert rv.json['info']['contact'] == contact
    assert rv.json['info']['license'] == license
    assert rv.json['info']['termsOfService'] == terms_of_service


@pytest.mark.parametrize('spec_format', ['json', 'yaml', 'yml'])
def test_spec_format(app, spec_format):
    app.config['SPEC_FORMAT'] = spec_format
    spec = app.spec
    if spec_format == 'json':
        assert isinstance(spec, dict)
    else:
        assert 'title: APIFlask' in spec


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


def test_auto_description(test_apps):
    from auto_description import app

    app.config['AUTO_DESCRIPTION'] = False

    spec = app.spec
    validate_spec(spec)
    assert 'description' not in spec['info']

    # reset the app status
    app._spec = None
    app.config['AUTO_DESCRIPTION'] = True


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_path_summary(app, client, config_value):
    app.config['AUTO_PATH_SUMMARY'] = config_value

    @app.get('/foo')
    def get_foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert rv.json['paths']['/foo']['get']['summary'] == 'Get Foo'
    else:
        assert 'summary' not in rv.json['paths']


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_path_description(app, client, config_value):
    app.config['AUTO_PATH_DESCRIPTION'] = config_value

    @app.get('/foo')
    def get_foo():
        """Get a Foo

        some description
        """
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert rv.json['paths']['/foo']['get']['description'] == 'some description'
    else:
        assert 'description' not in rv.json['paths']


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_200_response_for_bare_views(app, client, config_value):
    app.config['AUTO_200_RESPONSE'] = config_value

    @app.get('/foo')
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert bool('/foo' in rv.json['paths']) is config_value


@pytest.mark.parametrize('config_value', [True, False])
def test_auto_200_response_for_no_output_views(app, client, config_value):
    app.config['AUTO_200_RESPONSE'] = config_value

    @app.get('/bar')
    @input(QuerySchema, 'query')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/bar' in rv.json['paths']
    assert bool('200' in rv.json['paths']['/bar']['get']['responses']) is config_value


def test_response_description_config(app, client):
    app.config['DEFAULT_200_DESCRIPTION'] = 'It works'
    app.config['DEFAULT_204_DESCRIPTION'] = 'Nothing'

    @app.get('/foo')
    @input(FooSchema)
    def only_body_schema(foo):
        pass

    @app.get('/bar')
    @output(EmptySchema)
    def no_schema():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses'][
        '200']['description'] == 'It works'
    assert rv.json['paths']['/bar']['get']['responses'][
        '204']['description'] == 'Nothing'


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
        assert 'AuthorizationError' in rv.json['components']['schemas']
        assert '#/components/schemas/AuthorizationError' in \
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


@pytest.mark.parametrize('schema', [
    http_error_schema,
    AuthorizationErrorSchema
])
def test_auth_error_schema(app, client, schema):
    app.config['AUTH_ERROR_SCHEMA'] = schema
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['401']
    assert rv.json['paths']['/foo']['post']['responses']['401'][
        'description'] == 'Authorization error'
    assert 'AuthorizationError' in rv.json['components']['schemas']


def test_auth_error_schema_bad_type(app):
    app.config['AUTH_ERROR_SCHEMA'] = 'schema'
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @auth_required(auth)
    def foo():
        pass

    with pytest.raises(RuntimeError):
        app.spec


@pytest.mark.parametrize('config_value', [True, False])
def test_http_auth_error_response(app, client, config_value):
    app.config['AUTO_HTTP_ERROR_RESPONSE'] = config_value

    @app.get('/foo')
    @output(FooSchema)
    @doc(responses={204: 'empty', 400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    if config_value:
        assert 'HTTPError' in rv.json['components']['schemas']
        assert '#/components/schemas/HTTPError' in \
            rv.json['paths']['/foo']['get']['responses']['404'][
                'content']['application/json']['schema']['$ref']
        assert '#/components/schemas/HTTPError' in \
            rv.json['paths']['/foo']['get']['responses']['500'][
                'content']['application/json']['schema']['$ref']
        assert rv.json['paths']['/foo']['get']['responses']['204'][
                'content']['application/json']['schema'] == {}
    else:
        assert 'HTTPError' not in rv.json['components']['schemas']
        assert rv.json['paths']['/foo']['get']['responses']['404'][
                'content']['application/json']['schema'] == {}
        assert rv.json['paths']['/foo']['get']['responses']['500'][
                'content']['application/json']['schema'] == {}
        assert rv.json['paths']['/foo']['get']['responses']['204'][
                'content']['application/json']['schema'] == {}


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


def test_docs_hide_blueprints(app, client):
    bp = APIBlueprint('foo', __name__, tag='test')

    @bp.get('/foo')
    def foo():
        pass

    app.config['DOCS_HIDE_BLUEPRINTS'] = ['foo']
    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == []
    assert '/foo' not in rv.json['paths']


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
