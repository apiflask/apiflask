from dataclasses import dataclass

import openapi_spec_validator as osv
from flask import make_response
from flask.views import MethodView
from packaging.version import Version

from .conftest import APISPEC_VERSION
from .schemas import Foo
from .schemas import Query
from apiflask import Schema
from apiflask.fields import Field
from apiflask.fields import String


def test_output(app, client):
    @app.route('/foo')
    @app.output(Foo)
    def foo():
        return {'name': 'bar'}

    @app.route('/bar')
    @app.output(Foo, status_code=201)
    def bar():
        return {'name': 'foo'}

    @app.route('/baz')
    @app.input(Query, location='query')
    @app.output(Foo, status_code=201)
    def baz(query_data):
        if query_data['id'] == 1:
            return {'name': 'baz'}, 202
        elif query_data['id'] == 2:
            return {'name': 'baz'}, {'Location': '/baz'}
        elif query_data['id'] == 3:
            return {'name': 'baz'}, 202, {'Location': '/baz'}
        return ({'name': 'baz'},)

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json == {'id': 123, 'name': 'bar'}

    rv = client.get('/bar')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'foo'}

    rv = client.get('/baz')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers

    rv = client.get('/baz?id=2')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'].endswith('/baz')

    rv = client.get('/baz?id=3')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'].endswith('/baz')

    rv = client.get('/baz?id=4')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers


def test_output_with_methodview(app, client):
    @app.route('/')
    class FooAPI(MethodView):
        @app.output(Foo)
        def get(self):
            return {'name': 'bar'}

        @app.output(Foo, status_code=201)
        def post(self):
            return {'name': 'foo'}

        @app.input(Query, location='query')
        @app.output(Foo, status_code=201)
        def delete(self, query_data):
            if query_data['id'] == 1:
                return {'name': 'baz'}, 202
            elif query_data['id'] == 2:
                return {'name': 'baz'}, {'Location': '/baz'}
            elif query_data['id'] == 3:
                return {'name': 'baz'}, 202, {'Location': '/baz'}
            return ({'name': 'baz'},)

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json == {'id': 123, 'name': 'bar'}

    rv = client.post('/')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'foo'}

    rv = client.delete('/')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers

    rv = client.delete('/?id=2')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'].endswith('/baz')

    rv = client.delete('/?id=3')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'].endswith('/baz')

    rv = client.delete('/?id=4')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers


def test_output_with_dict_schema(app, client):
    dict_schema = {'name': String(dump_default='grey')}

    @app.get('/foo')
    @app.output(dict_schema, schema_name='MyName')
    def foo():
        return ''

    @app.get('/bar')
    @app.output(dict_schema, schema_name='MyName')
    def bar():
        return {'name': 'peter'}

    @app.get('/baz')
    @app.output(dict_schema)
    def baz():
        pass

    @app.get('/spam')
    @app.output(dict_schema)
    def spam():
        pass

    @app.get('/eggs')
    @app.output({})
    def eggs():
        pass

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json == {'name': 'grey'}

    rv = client.get('/bar')
    assert rv.status_code == 200
    assert rv.json == {'name': 'peter'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert (
        rv.json['paths']['/foo']['get']['responses']['200']['content']['application/json'][
            'schema'
        ]['$ref']
        == '#/components/schemas/MyName'
    )

    # Check schema fields individually to avoid ordering issues
    schema = rv.json['components']['schemas']['MyName']
    assert schema['type'] == 'object'
    assert schema['properties'] == {'name': {'type': 'string'}}
    # In apispec >= 6.8.3, additionalProperties should be False (or omitted, treated as False)
    if APISPEC_VERSION >= Version('6.8.3'):
        assert schema.get('additionalProperties', False) is False
    else:
        assert 'additionalProperties' not in schema
    assert (
        rv.json['paths']['/bar']['get']['responses']['200']['content']['application/json'][
            'schema'
        ]['$ref']
        == '#/components/schemas/MyName1'
    )
    # default schema name is "Generated"
    assert (
        rv.json['paths']['/baz']['get']['responses']['200']['content']['application/json'][
            'schema'
        ]['$ref']
        == '#/components/schemas/GeneratedSchema'
    )
    assert (
        rv.json['paths']['/spam']['get']['responses']['200']['content']['application/json'][
            'schema'
        ]['$ref']
        == '#/components/schemas/GeneratedSchema1'
    )


def test_output_with_object_schema(app, client):
    class BaseResponse(Schema):
        data = Field()
        message = String(dump_default='Success')

    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse

    class PetOut(Schema):
        name = String()

    @dataclass
    class Pet:
        name: str

    @dataclass
    class Response:
        data: Pet

    @app.get('/foo')
    @app.output(PetOut)
    def foo():
        pet = Pet('foo')
        return Response(data=pet)

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json['data'] == {'name': 'foo'}


def test_output_body_example(app, client):
    example = {'name': 'foo', 'id': 2}
    examples = {
        'example foo': {'summary': 'an example of foo', 'value': {'name': 'foo', 'id': 1}},
        'example bar': {'summary': 'an example of bar', 'value': {'name': 'bar', 'id': 2}},
    }

    @app.get('/foo')
    @app.output(Foo, example=example)
    def foo():
        pass

    @app.get('/bar')
    @app.output(Foo, examples=examples)
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert (
        rv.json['paths']['/foo']['get']['responses']['200']['content']['application/json'][
            'example'
        ]
        == example
    )
    assert (
        rv.json['paths']['/bar']['get']['responses']['200']['content']['application/json'][
            'examples'
        ]
        == examples
    )


def test_output_with_empty_dict_as_schema(app, client):
    @app.delete('/foo')
    @app.output({}, status_code=204)
    def delete_foo():
        return ''

    @app.route('/bar')
    class Bar(MethodView):
        @app.output({}, status_code=204)
        def delete(self):
            return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'content' not in rv.json['paths']['/foo']['delete']['responses']['204']
    assert 'content' not in rv.json['paths']['/bar']['delete']['responses']['204']

    rv = client.delete('/foo')
    assert rv.status_code == 204
    rv = client.delete('/bar')
    assert rv.status_code == 204


def test_output_response_object_directly(app, client):
    @app.get('/foo')
    @app.output(Foo)
    def foo():
        return make_response({'message': 'hello'})

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json['message'] == 'hello'


def test_response_links(app, client):
    links = {
        'foo': {'operationId': 'getFoo', 'parameters': {'id': '$response.body#/id'}},
        'bar': {'operationId': 'getBar', 'parameters': {'id': '$response.body#/id'}},
    }

    @app.get('/foo')
    @app.output(Foo, links=links)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['200']['links'] == links


def test_response_links_ref(app, client):
    links = {'getFoo': {'$ref': '#/components/links/foo'}}

    @app.spec_processor
    def add_links(spec):
        spec['components']['links'] = {
            'foo': {'operationId': 'getFoo', 'parameters': {'id': '$response.body#/id'}}
        }
        return spec

    @app.get('/foo')
    @app.output(Foo, links=links)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'getFoo' in rv.json['paths']['/foo']['get']['responses']['200']['links']


def test_response_content_type(app, client):
    @app.get('/foo')
    @app.output(Foo)  # default value is application/json
    def foo():
        pass

    @app.get('/bar')
    @app.output(Foo, content_type='image/png')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert len(rv.json['paths']['/foo']['get']['responses']['200']['content']) == 1
    assert len(rv.json['paths']['/bar']['get']['responses']['200']['content']) == 1
    assert 'application/json' in rv.json['paths']['/foo']['get']['responses']['200']['content']
    assert 'image/png' in rv.json['paths']['/bar']['get']['responses']['200']['content']
