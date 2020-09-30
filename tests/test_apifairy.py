import unittest

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE

from apifairy import APIFairy, body, arguments, response, authenticate


class TestAPIFairy(unittest.TestCase):
    def test_body(self):
        app = Flask(__name__)
        ma = Marshmallow(app)
        APIFairy(app)

        class Schema(ma.Schema):
            id = ma.Integer()
            name = ma.Str(required=True)

        @app.route('/foo', methods=['POST'])
        @body(Schema())
        def foo(schema):
            return schema

        client = app.test_client()

        rv = client.post('/foo')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'json': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo', json={'id': 1})
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'json': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo', json={'id': 1, 'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'id': 1, 'name': 'bar'}

        rv = client.post('/foo', json={'name': 'bar'})
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar'}

    def test_query(self):
        app = Flask(__name__)
        ma = Marshmallow(app)
        apifairy = APIFairy()
        apifairy.init_app(app)

        class Schema(ma.Schema):
            class Meta:
                unknown = EXCLUDE

            id = ma.Integer()
            name = ma.Str(required=True)

        class Schema2(ma.Schema):
            class Meta:
                unknown = EXCLUDE

            id2 = ma.Integer()
            name2 = ma.Str(required=True)

        @app.route('/foo', methods=['POST'])
        @arguments(Schema())
        @arguments(Schema2())
        def foo(schema, schema2):
            return {'name': schema['name'], 'name2': schema2['name2']}

        client = app.test_client()

        rv = client.post('/foo')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'query': {'name': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo?id=1&name=bar')
        assert rv.status_code == 400
        assert rv.json == {
            'messages': {
                'query': {'name2': ['Missing data for required field.']}
            }
        }

        rv = client.post('/foo?id=1&name=bar&id2=2&name2=baz')
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar', 'name2': 'baz'}

        rv = client.post('/foo?name=bar&name2=baz')
        assert rv.status_code == 200
        assert rv.json == {'name': 'bar', 'name2': 'baz'}

    def test_response(self):
        app = Flask(__name__)
        ma = Marshmallow(app)
        APIFairy(app)

        class Schema(ma.Schema):
            id = ma.Integer(default=123)
            name = ma.Str()

        class QuerySchema(ma.Schema):
            id = ma.Integer(missing=1)

        @app.route('/foo')
        @response(Schema())
        def foo():
            return {'name': 'bar'}

        @app.route('/bar')
        @response(Schema(), status_code=201)
        def bar():
            return {'name': 'foo'}

        @app.route('/baz')
        @arguments(QuerySchema)
        @response(Schema(), status_code=201)
        def baz(query):
            if query['id'] == 1:
                return {'name': 'foo'}, 202
            elif query['id'] == 2:
                return {'name': 'foo'}, {'Location': '/baz'}
            elif query['id'] == 3:
                return {'name': 'foo'}, 202, {'Location': '/baz'}
            return ({'name': 'foo'},)

        client = app.test_client()

        rv = client.get('/foo')
        assert rv.status_code == 200
        assert rv.json == {'id': 123, 'name': 'bar'}

        rv = client.get('/bar')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'foo'}

        rv = client.get('/baz')
        assert rv.status_code == 202
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert 'Location' not in rv.headers

        rv = client.get('/baz?id=2')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert rv.headers['Location'] == 'http://localhost/baz'

        rv = client.get('/baz?id=3')
        assert rv.status_code == 202
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert rv.headers['Location'] == 'http://localhost/baz'

        rv = client.get('/baz?id=4')
        assert rv.status_code == 200
        assert rv.json == {'id': 123, 'name': 'foo'}
        assert 'Location' not in rv.headers

    def test_authenticate(self):
        app = Flask(__name__)
        auth = HTTPBasicAuth()
        APIFairy(app)

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
        @authenticate(auth)
        def foo():
            return auth.current_user()

        @app.route('/bar')
        @authenticate(auth, role='admin')
        def bar():
            return auth.current_user()

        client = app.test_client()

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
