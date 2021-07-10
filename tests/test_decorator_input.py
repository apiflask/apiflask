import pytest
from flask.views import MethodView
from openapi_spec_validator import validate_spec

from .schemas import BarSchema
from .schemas import FooSchema
from .schemas import QuerySchema
from apiflask import input
from apiflask.fields import String


def test_input(app, client):
    @app.route('/foo', methods=['POST'])
    @input(FooSchema)
    def foo(schema):
        return schema

    @app.route('/bar')
    class Bar(MethodView):
        @input(FooSchema)
        def post(self, data):
            return data

    for rule in ['/foo', '/bar']:
        rv = client.post(rule)
        assert rv.status_code == 400
        assert rv.json == {
            'detail': {
                'json': {'name': ['Missing data for required field.']}
            },
            'message': 'Validation error',
            'status_code': 400
        }

        rv = client.post(rule, json={'id': 1})
        assert rv.status_code == 400
        assert rv.json == {
            'detail': {
                'json': {'name': ['Missing data for required field.']}
            },
            'message': 'Validation error',
            'status_code': 400
        }

        rv = client.post(rule, json={'id': 1, 'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'id': 1, 'name': 'bar'}

        rv = client.post(rule, json={'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar'}

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths'][rule]['post']['requestBody'][
            'content']['application/json']['schema']['$ref'] == '#/components/schemas/Foo'


def test_input_with_query_location(app, client):
    @app.route('/foo', methods=['POST'])
    @input(FooSchema, location='query')
    @input(BarSchema, location='query')
    def foo(schema, schema2):
        return {'name': schema['name'], 'name2': schema2['name2']}

    rv = client.post('/foo')
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'query': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.post('/foo?id=1&name=bar')
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'query': {'name2': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.post('/foo?id=1&name=bar&id2=2&name2=baz')
    assert rv.status_code == 200
    assert rv.json == {'name': 'bar', 'name2': 'baz'}

    rv = client.post('/foo?name=bar&name2=baz')
    assert rv.status_code == 200
    assert rv.json == {'name': 'bar', 'name2': 'baz'}


def test_bad_input_location(app):
    with pytest.raises(ValueError):
        @app.route('/foo')
        @input(QuerySchema, 'bad')
        def foo(query):
            pass


def test_input_with_dict_schema(app, client):
    dict_schema = {
        'name': String(required=True)
    }

    @app.get('/foo')
    @input(dict_schema, 'query')
    def foo(query):
        return query

    @app.post('/bar')
    @input(dict_schema, schema_name='MyName')
    def bar(body):
        return body

    @app.post('/baz')
    @input(dict_schema)
    def baz(body):
        return body

    @app.post('/spam')
    @input(dict_schema)
    def spam(body):
        return body

    rv = client.get('/foo')
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'query': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.get('/foo?name=grey')
    assert rv.status_code == 200
    assert rv.json == {'name': 'grey'}

    rv = client.post('/bar')
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'json': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.post('/bar', json={'name': 'grey'})
    assert rv.status_code == 200
    assert rv.json == {'name': 'grey'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['parameters'][0] == {
        'in': 'query',
        'name': 'name',
        'required': True,
        'schema': {
            'type': 'string'
        }
    }
    # TODO check the excess item "'x-scope': ['']" in schema object
    assert rv.json['paths']['/bar']['post']['requestBody'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/MyName'
    assert rv.json['components']['schemas']['MyName'] == {
        'properties': {
            'name': {
                'type': 'string'
            }
        },
        'required': ['name'],
        'type': 'object'
    }
    # default schema name is "Generated"
    assert rv.json['paths']['/baz']['post']['requestBody'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/Generated'
    assert rv.json['paths']['/spam']['post']['requestBody'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/Generated1'


def test_input_body_example(app, client):
    example = {'name': 'foo', 'id': 2}
    examples = {
        'example foo': {
            'summary': 'an example of foo',
            'value': {'name': 'foo', 'id': 1}
        },
        'example bar': {
            'summary': 'an example of bar',
            'value': {'name': 'bar', 'id': 2}
        },
    }

    @app.post('/foo')
    @input(FooSchema, example=example)
    def foo():
        pass

    @app.post('/bar')
    @input(FooSchema, examples=examples)
    def bar():
        pass

    @app.route('/baz')
    class Baz(MethodView):
        @input(FooSchema, example=example)
        def get(self):
            pass

        @input(FooSchema, examples=examples)
        def post(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['requestBody'][
        'content']['application/json']['example'] == example
    assert rv.json['paths']['/bar']['post']['requestBody'][
        'content']['application/json']['examples'] == examples

    assert rv.json['paths']['/baz']['get']['requestBody'][
        'content']['application/json']['example'] == example
    assert rv.json['paths']['/baz']['post']['requestBody'][
        'content']['application/json']['examples'] == examples
