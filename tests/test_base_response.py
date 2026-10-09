import openapi_spec_validator as osv
import pytest

from .schemas import Foo
from apiflask import Schema
from apiflask.fields import Field
from apiflask.fields import Integer
from apiflask.fields import String


class BaseResponse(Schema):
    message = String()
    status_code = Integer()
    data = Field()


class NullableBaseResponse(Schema):
    message = String(allow_none=True)
    data = Field()


class BadBaseResponse(Schema):
    message = String()
    status_code = Integer()
    some_data = Field()


base_response_schema_dict = {
    'properties': {
        'data': {'type': 'object'},
        'message': {'type': 'string'},
        'status_code': {'type': 'integer'},
    },
    'type': 'object',
}

bad_base_response_schema_dict = {
    'properties': {
        'some_data': {'type': 'object'},
        'message': {'type': 'string'},
        'status_code': {'type': 'integer'},
    },
    'type': 'object',
}


def test_output_base_response(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    @app.get('/')
    @app.output(Foo)
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
        BaseResponse,
        base_response_schema_dict,
        BadBaseResponse,
        bad_base_response_schema_dict,
        '',
        None,
    ],
)
def test_base_response_spec(app, client, base_schema):
    app.config['BASE_RESPONSE_SCHEMA'] = base_schema

    @app.get('/')
    @app.output(Foo)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    if base_schema == '':
        with pytest.raises(TypeError) as e:
            app.spec
        assert 'marshmallow' in str(e.value)
    elif base_schema in [BadBaseResponse, bad_base_response_schema_dict]:
        with pytest.raises(RuntimeError) as e:
            app.spec
        assert 'data key' in str(e.value)
    else:
        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        osv.validate(rv.json)
        schema = rv.json['paths']['/']['get']['responses']['200']['content']['application/json'][
            'schema'
        ]
        schema_ref = '#/components/schemas/Foo'
        # TODO the output schema ref contains unused `'x-scope': ['']` field
        # it seems related to openapi-spec-validator:
        # https://github.com/p1c2u/openapi-spec-validator/issues/53
        if base_schema in [BaseResponse, base_response_schema_dict]:
            properties = schema['properties']
            assert properties['data']['$ref'] == schema_ref
            assert properties['status_code'] == {'type': 'integer'}
            assert properties['message'] == {'type': 'string'}
        elif base_schema is None:
            assert schema['$ref'] == schema_ref


def test_base_response_data_key(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse
    app.config['BASE_RESPONSE_DATA_KEY '] = 'data'

    @app.get('/')
    @app.output(Foo)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'info': data}

    with app.test_request_context('/'):
        with pytest.raises(RuntimeError, match=r'The data key.*is not found in the returned dict.'):
            foo()


def test_base_response_204(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    @app.get('/')
    @app.output({}, status_code=204)
    def foo():
        return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'content' not in rv.json['paths']['/']['get']['responses']['204']


def test_base_response_many(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    @app.get('/')
    @app.output(Foo(many=True))
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json
    assert 'data' in rv.json
    assert not isinstance(rv.json, list)
    assert isinstance(rv.json['data'], list)


def test_bare_view_base_response_spec(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    @app.get('/')
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    schema = rv.json['paths']['/']['get']['responses']['200']['content']['application/json'][
        'schema'
    ]
    assert schema['properties']['status_code'] == {'type': 'integer'}
    assert schema['properties']['message'] == {'type': 'string'}


def test_input_with_base_response_spec(app, client):
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    @app.get('/')
    @app.input(Foo)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': 'Success.', 'status_code': '200', 'data': data}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    schema = rv.json['paths']['/']['get']['responses']['200']['content']['application/json'][
        'schema'
    ]
    assert schema['properties']['status_code'] == {'type': 'integer'}
    assert schema['properties']['message'] == {'type': 'string'}


@pytest.mark.parametrize('openapi_version', ['3.0.3', '3.1.0'])
def test_base_response_nullable_follows_openapi_version(app, client, openapi_version):
    app.config['OPENAPI_VERSION'] = openapi_version
    app.config['BASE_RESPONSE_SCHEMA'] = NullableBaseResponse

    @app.get('/')
    @app.output(Foo)
    def foo():
        data = {'id': '123', 'name': 'test'}
        return {'message': None, 'data': data}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    schema = rv.json['paths']['/']['get']['responses']['200']['content']['application/json'][
        'schema'
    ]
    message = schema['properties']['message']
    if openapi_version == '3.1.0':
        assert message['type'] == ['string', 'null']
        assert 'nullable' not in message
    else:
        assert message['type'] == 'string'
        assert message['nullable'] is True
