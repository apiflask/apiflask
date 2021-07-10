import pytest
from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from apiflask import output
from apiflask import Schema
from apiflask.fields import Field
from apiflask.fields import Integer
from apiflask.fields import String


class BaseResponseSchema(Schema):
    message = String()
    status_code = Integer()
    data = Field()


class BadBaseResponseSchema(Schema):
    message = String()
    status_code = Integer()
    some_data = Field()


base_response_schema_dict = {
    "properties": {
        "data": {
            "type": "object"
        },
        "message": {
            "type": "string"
        },
        "status_code": {
            "type": "integer"
        }
    },
    "type": "object"
}

bad_base_response_schema_dict = {
    "properties": {
        "some_data": {
            "type": "object"
        },
        "message": {
            "type": "string"
        },
        "status_code": {
            "type": "integer"
        }
    },
    "type": "object"
}


def test_output_base_response(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema

    @app.get('/')
    @output(FooSchema)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json
    assert 'data' in rv.json
    assert rv.json['message'] == 'Success.'
    assert rv.json['status_code'] == 200
    assert rv.json['data']['id'] == 123
    assert rv.json['data']['name'] == 'test'


@pytest.mark.parametrize(
    'base_schema',
    [
        BaseResponseSchema,
        base_response_schema_dict,
        BadBaseResponseSchema,
        bad_base_response_schema_dict,
        '',
        None
    ]
)
def test_base_response_spec(app, client, base_schema):
    app.config['BASE_RESPONSE_SCHEMA'] = base_schema

    @app.get('/')
    @output(FooSchema)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    if base_schema == '':
        with pytest.raises(TypeError) as e:
            app.spec
        assert 'Marshmallow' in str(e.value)
    elif base_schema in [BadBaseResponseSchema, bad_base_response_schema_dict]:
        with pytest.raises(RuntimeError) as e:
            app.spec
        assert 'data key' in str(e.value)
    else:
        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        schema = rv.json['paths']['/']['get']['responses']['200']['content'][
            'application/json']['schema']
        schema_ref = '#/components/schemas/Foo'
        # TODO the output schema ref contains unused `'x-scope': ['']` field
        if base_schema in [BaseResponseSchema, base_response_schema_dict]:
            properties = schema['properties']
            assert properties['data']['$ref'] == schema_ref
            assert properties['status_code'] == {'type': 'integer'}
            assert properties['message'] == {'type': 'string'}
        elif base_schema is None:
            assert schema['$ref'] == schema_ref


# TODO pytest seems can't catch the ValueError happened in the output decorator
def test_base_response_data_key(app, client):
    pytest.skip()

    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
    app.config['BASE_RESPONSE_DATA_KEY '] = 'data'

    @app.get('/')
    @output(FooSchema)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'info': data}

    with pytest.raises(ValueError):
        client.get('/')


def test_base_response_204(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema

    @app.get('/')
    @output({}, 204)
    def foo():
        return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'content' not in rv.json['paths']['/']['get']['responses']['204']


def test_base_response_many(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema

    @app.get('/')
    @output(FooSchema(many=True))
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json
    assert 'data' in rv.json
    assert not isinstance(rv.json, list)
    assert isinstance(rv.json['data'], list)
