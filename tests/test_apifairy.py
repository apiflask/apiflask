import unittest

from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE

from apifairy import APIFairy, body, arguments, response


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
        APIFairy(app)

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

        @app.route('/foo')
        @response(Schema(), status_code=201)
        def foo():
            return {'name': 'bar'}

        client = app.test_client()

        rv = client.get('/foo')
        assert rv.status_code == 201
        assert rv.json == {'id': 123, 'name': 'bar'}
