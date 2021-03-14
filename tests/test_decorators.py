from flask_httpauth import HTTPBasicAuth

from apiflask import input, output, auth_required

from .schemas import FooSchema, BarSchema, QuerySchema


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


def test_query(app, client):

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


def test_response(app, client):

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


def test_authenticate(app, client):

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
        return auth.current_user()

    @app.route('/bar')
    @auth_required(auth, role='admin')
    def bar():
        return auth.current_user()

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/foo',
                    headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.get('/bar',
                    headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/foo',
                    headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar',
                    headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
