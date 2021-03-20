import pytest
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint, input, output, auth_required, doc
from apiflask.security import HTTPBasicAuth, HTTPTokenAuth

from .schemas import FooSchema, BarSchema, QuerySchema


def test_auth_required(app, client):
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        if username == 'foo' and password == 'bar':
            return {'user': 'foo'}
        elif username == 'bar' and password == 'foo':
            return {'user': 'bar'}

    @auth.get_user_roles
    def get_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        return 'normal'

    @app.route('/foo')
    @auth_required(auth)
    def foo():
        return auth.current_user

    @app.route('/bar')
    @auth_required(auth, role='admin')
    def bar():
        return auth.current_user

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/foo', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.get('/bar', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}


def test_auth_required_at_blueprint_before_request(app, client):
    bp = APIBlueprint('test', __name__)

    auth = HTTPTokenAuth()

    @bp.before_request
    @auth_required(auth)
    def before():
        pass

    @bp.get('/foo')
    def foo():
        pass

    @bp.get('/bar')
    def bar():
        pass

    app.register_blueprint(bp)

    rv = client.get('/foo')
    assert rv.status_code == 401
    rv = client.get('/bar')
    assert rv.status_code == 401

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'scheme': 'Bearer',
        'type': 'http'
    }

    assert 'BearerAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'BearerAuth' in rv.json['paths']['/bar']['get']['security'][0]


def test_input(app, client):
    @app.route('/foo', methods=['POST'])
    @input(FooSchema)
    def foo(schema):
        return schema

    rv = client.post('/foo')
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'json': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.post('/foo', json={'id': 1})
    assert rv.status_code == 400
    assert rv.json == {
        'detail': {
            'json': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error',
        'status_code': 400
    }

    rv = client.post('/foo', json={'id': 1, 'name': 'bar'})
    assert rv.status_code == 200
    assert rv.json == {'id': 1, 'name': 'bar'}

    rv = client.post('/foo', json={'name': 'bar'})
    assert rv.status_code == 200
    assert rv.json == {'name': 'bar'}


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
    with pytest.raises(RuntimeError):
        @app.route('/foo')
        @input(QuerySchema, 'bad')
        def foo(query):
            pass


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


def test_doc_summary_and_description(app, client):
    @app.route('/foo')
    @doc(summary='summary from doc decorator')
    def foo():
        pass

    @app.route('/bar')
    @doc(summary='summary for bar', description='some description for bar')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['summary'] == 'summary from doc decorator'
    assert 'description' not in rv.json['paths']['/foo']['get']
    assert rv.json['paths']['/bar']['get']['summary'] == 'summary for bar'
    assert rv.json['paths']['/bar']['get']['description'] == 'some description for bar'


def test_doc_tags(app, client):
    app.tags = ['foo', 'bar']

    @app.route('/foo')
    @doc(tags='foo')
    def foo():
        pass

    @app.route('/bar')
    @doc(tags=['foo', 'bar'])
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['tags'] == ['foo']
    assert rv.json['paths']['/bar']['get']['tags'] == ['foo', 'bar']


def test_doc_hide(app, client):
    @app.route('/foo')
    @doc(hide=True)
    def foo():
        pass

    @app.get('/baz')
    def get_baz():
        pass

    @app.post('/baz')
    @doc(hide=True)
    def post_baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/foo' not in rv.json['paths']
    assert '/baz' in rv.json['paths']
    assert 'get' in rv.json['paths']['/baz']
    assert 'post' not in rv.json['paths']['/baz']


def test_doc_deprecated(app, client):
    @app.route('/foo')
    @doc(deprecated=True)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['deprecated']


def test_doc_responses(app, client):
    @app.route('/foo')
    @output(FooSchema)
    @doc(responses={400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '200' in rv.json['paths']['/foo']['get']['responses']
    assert '400' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses']['400']['description'] == 'bad'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses']['404']['description'] == 'not found'
    assert '500' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses']['500']['description'] == 'server error'
