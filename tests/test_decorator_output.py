from flask import make_response
from flask.views import MethodView
from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from .schemas import QuerySchema
from apiflask import input
from apiflask import output
from apiflask.fields import String


def test_output(app, client):
    @app.route('/foo')
    @output(FooSchema)
    def foo():
        return {'name': 'bar'}

    @app.route('/bar')
    @output(FooSchema, status_code=201)
    def bar():
        return {'name': 'foo'}

    @app.route('/baz')
    @input(QuerySchema, 'query')
    @output(FooSchema, status_code=201)
    def baz(query):
        if query['id'] == 1:
            return {'name': 'baz'}, 202
        elif query['id'] == 2:
            return {'name': 'baz'}, {'Location': '/baz'}
        elif query['id'] == 3:
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
    assert rv.headers['Location'] == 'http://localhost/baz'

    rv = client.get('/baz?id=3')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'] == 'http://localhost/baz'

    rv = client.get('/baz?id=4')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers


def test_output_with_methodview(app, client):
    @app.route('/')
    class Foo(MethodView):
        @output(FooSchema)
        def get(self):
            return {'name': 'bar'}

        @output(FooSchema, status_code=201)
        def post(self):
            return {'name': 'foo'}

        @input(QuerySchema, 'query')
        @output(FooSchema, status_code=201)
        def delete(self, query):
            if query['id'] == 1:
                return {'name': 'baz'}, 202
            elif query['id'] == 2:
                return {'name': 'baz'}, {'Location': '/baz'}
            elif query['id'] == 3:
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
    assert rv.headers['Location'] == 'http://localhost/baz'

    rv = client.delete('/?id=3')
    assert rv.status_code == 202
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert rv.headers['Location'] == 'http://localhost/baz'

    rv = client.delete('/?id=4')
    assert rv.status_code == 201
    assert rv.json == {'id': 123, 'name': 'baz'}
    assert 'Location' not in rv.headers


def test_output_with_dict_schema(app, client):
    dict_schema = {
        'name': String(default='grey')
    }

    @app.get('/foo')
    @output(dict_schema, schema_name='MyName')
    def foo():
        return ''

    @app.get('/bar')
    @output(dict_schema, schema_name='MyName')
    def bar():
        return {'name': 'peter'}

    @app.get('/baz')
    @output(dict_schema)
    def baz():
        pass

    @app.get('/spam')
    @output(dict_schema)
    def spam():
        pass

    @app.get('/eggs')
    @output({})
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
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['200'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/MyName'
    assert rv.json['components']['schemas']['MyName'] == {
        'properties': {
            'name': {
                'type': 'string'
            }
        },
        'type': 'object'
    }
    assert rv.json['paths']['/bar']['get']['responses']['200'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/MyName1'
    # default schema name is "Generated"
    assert rv.json['paths']['/baz']['get']['responses']['200'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/Generated'
    assert rv.json['paths']['/spam']['get']['responses']['200'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/Generated1'


def test_output_body_example(app, client):
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

    @app.get('/foo')
    @output(FooSchema, example=example)
    def foo():
        pass

    @app.get('/bar')
    @output(FooSchema, examples=examples)
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['200'][
        'content']['application/json']['example'] == example
    assert rv.json['paths']['/bar']['get']['responses']['200'][
        'content']['application/json']['examples'] == examples


def test_output_with_empty_dict_as_schema(app, client):
    @app.delete('/foo')
    @output({}, 204)
    def delete_foo():
        return ''

    @app.route('/bar')
    class Bar(MethodView):
        @output({}, 204)
        def delete(self):
            return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'content' not in rv.json['paths']['/foo']['delete']['responses']['204']
    assert 'content' not in rv.json['paths']['/bar']['delete']['responses']['204']

    rv = client.delete('/foo')
    assert rv.status_code == 204
    rv = client.delete('/bar')
    assert rv.status_code == 204


def test_output_response_object_directly(app, client):
    @app.get('/foo')
    @output(FooSchema)
    def foo():
        return make_response({'message': 'hello'})

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json['message'] == 'hello'
