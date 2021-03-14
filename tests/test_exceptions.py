from openapi_spec_validator import validate_spec

from apiflask import input
from .schemas import FooSchema


def test_register_validation_error_response(app, client):

    error_code = str(app.config['VALIDATION_ERROR_CODE'])

    @app.post('/foo')
    @input(FooSchema)
    def foo():
        pass

    @app.get('/bar')
    @input(FooSchema, 'query')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['responses'][
        error_code] is not None
    assert rv.json['paths']['/foo']['post']['responses'][
        error_code]['description'] == 'Validation error'
    assert rv.json['paths']['/bar']['get']['responses'][
        error_code] is not None
    assert rv.json['paths']['/bar']['get']['responses'][
        error_code]['description'] == 'Validation error'


def test_validation_error_config(app, client):

    app.config['VALIDATION_ERROR_CODE'] = 422
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
