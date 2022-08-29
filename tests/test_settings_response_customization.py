import pytest
from openapi_spec_validator import validate_spec

from .schemas import Foo
from .schemas import HTTPError
from .schemas import ValidationError
from apiflask.schemas import EmptySchema
from apiflask.schemas import http_error_schema
from apiflask.security import HTTPBasicAuth


def test_response_description_config(app, client):
    app.config['SUCCESS_DESCRIPTION'] = 'Success'
    app.config['NOT_FOUND_DESCRIPTION'] = 'Egg not found'

    @app.get('/foo')
    @app.input(Foo)  # 200
    def only_body_schema(foo):
        pass

    @app.get('/bar')
    @app.output(Foo, status_code=201)
    def create():
        pass

    @app.get('/baz')
    @app.output(EmptySchema)  # 204
    def no_schema():
        pass

    @app.get('/spam')
    @app.output(Foo, status_code=206)
    def spam():
        pass

    @app.get('/eggs/<int:id>')
    def eggs():
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
    assert rv.json['paths']['/eggs/{id}']['get']['responses'][
        '404']['description'] == 'Egg not found'


def test_validation_error_status_code_and_description(app, client):
    app.config['VALIDATION_ERROR_STATUS_CODE'] = 400
    app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Bad'

    @app.post('/foo')
    @app.input(Foo)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['400'] is not None
    assert rv.json['paths']['/foo']['post']['responses'][
        '400']['description'] == 'Bad'


@pytest.mark.parametrize('schema', [
    http_error_schema,
    ValidationError
])
def test_validation_error_schema(app, client, schema):
    app.config['VALIDATION_ERROR_SCHEMA'] = schema

    @app.post('/foo')
    @app.input(Foo)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['422']
    assert rv.json['paths']['/foo']['post']['responses']['422'][
        'description'] == 'Validation error'
    assert 'ValidationError' in rv.json['components']['schemas']


def test_validation_error_schema_bad_type(app):
    app.config['VALIDATION_ERROR_SCHEMA'] = 'schema'

    @app.post('/foo')
    @app.input(Foo)
    def foo():
        pass

    with pytest.raises(TypeError):
        app.spec


def test_auth_error_status_code_and_description(app, client):
    app.config['AUTH_ERROR_STATUS_CODE'] = 403
    app.config['AUTH_ERROR_DESCRIPTION'] = 'Bad'
    auth = HTTPBasicAuth()

    @app.post('/foo')
    @app.auth_required(auth)
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
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses']['401']
    assert 'HTTPError' in rv.json['components']['schemas']


def test_http_auth_error_response(app, client):
    @app.get('/foo')
    @app.output(Foo)
    @app.doc(responses={204: 'empty', 400: 'bad', 404: 'not found', 500: 'server error'})
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
    HTTPError
])
def test_http_error_schema(app, client, schema):
    app.config['HTTP_ERROR_SCHEMA'] = schema

    @app.get('/foo')
    @app.output(Foo)
    @app.doc(responses={400: 'bad', 404: 'not found', 500: 'server error'})
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
    @app.output(Foo)
    @app.doc(responses={400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    with pytest.raises(TypeError):
        app.spec
