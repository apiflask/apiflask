import unittest

from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE
from openapi_spec_validator import validate_spec

from apiflask import APIFlask, body, arguments, response, authenticate, \
    other_responses

ma = Marshmallow()


class Schema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    id = ma.Integer(default=123)
    name = ma.Str(required=True)


class Schema2(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    id2 = ma.Integer(default=123)
    name2 = ma.Str(required=True)


class FooSchema(ma.Schema):
    id = ma.Integer(default=123)
    name = ma.Str()


class QuerySchema(ma.Schema):
    id = ma.Integer(missing=1)


class TestAPIFlask(unittest.TestCase):
    def create_app(self):
        app = APIFlask(__name__)
        app.config['OPENAPI_TITLE'] = 'Foo'
        app.config['OPENAPI_VERSION'] = '1.0'
        ma.init_app(app)
        return app

    def test_body(self):
        app = self.create_app()

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
        app = self.create_app()

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
        app = self.create_app()

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
        app = self.create_app()
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

    def test_apispec(self):
        app = self.create_app()
        auth = HTTPBasicAuth()

        @app.process_apispec
        def edit_apispec(apispec):
            assert apispec['openapi'] == '3.0.3'
            apispec['openapi'] = '3.0.2'
            return apispec

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
        @arguments(QuerySchema)
        @body(Schema)
        @response(Schema)
        @other_responses({404: 'foo not found'})
        def foo():
            return {'id': 123, 'name': auth.current_user()['user']}

        client = app.test_client()

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert app.config['OPENAPI_TITLE'] == 'Foo'
        assert rv.json['openapi'] == '3.0.2'
        assert rv.json['info']['title'] == 'Foo'
        assert rv.json['info']['version'] == '1.0'

        assert app.apispec is app.apispec

        rv = client.get('/docs')
        assert rv.status_code == 200
        assert b'swagger-ui-standalone-preset.js' in rv.data

        rv = client.get('/redoc')
        assert rv.status_code == 200
        assert b'redoc.standalone.js' in rv.data

    def test_apispec_schemas(self):
        app = self.create_app()

        @app.route('/foo')
        @response(Schema(partial=True))
        def foo():
            pass

        @app.route('/bar')
        @response(Schema2(many=True))
        def bar():
            pass

        @app.route('/baz')
        @response(FooSchema)
        def baz():
            pass

        with app.app_context():
            apispec = app.apispec
        assert len(apispec['components']['schemas']) == 3
        assert 'SchemaUpdate' in apispec['components']['schemas']
        assert 'Schema2List' in apispec['components']['schemas']
        assert 'Foo' in apispec['components']['schemas']

    def test_apispec_path_summary_description_from_docs(self):
        app = self.create_app()

        @app.route('/users')
        @response(Schema)
        def get_users():
            """Get Users"""
            pass

        @app.route('/users/<id>', methods=['PUT'])
        @response(Schema)
        def update_user(id):
            """
            Update User

            Update a user with specified ID.
            """
            pass

        client = app.test_client()

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/users']['get']['summary'] == 'Get Users'
        assert rv.json['paths']['/users/{id}']['put']['summary'] == \
            'Update User'
        assert rv.json['paths']['/users/{id}']['put']['description'] == \
            'Update a user with specified ID.'

    def test_apispec_path_parameters_registration(self):
        app = self.create_app()

        @app.route('/strings/<some_string>')
        @response(Schema)
        def get_string(some_string):
            pass

        @app.route('/floats/<float:some_float>', methods=['POST'])
        @response(Schema)
        def get_float(some_float):
            pass

        @app.route('/integers/<int:some_integer>', methods=['PUT'])
        @response(Schema)
        def get_integer(some_integer):
            pass

        @app.route('/users/<int:user_id>/articles/<int:article_id>')
        @response(Schema)
        def get_article(user_id, article_id):
            pass

        client = app.test_client()

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['in'] == 'path'
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['name'] == 'some_string'
        assert rv.json['paths']['/strings/{some_string}'][
            'get']['parameters'][0]['schema']['type'] == 'string'
        assert rv.json['paths']['/floats/{some_float}'][
            'post']['parameters'][0]['schema']['type'] == 'number'
        assert rv.json['paths']['/integers/{some_integer}'][
            'put']['parameters'][0]['schema']['type'] == 'integer'
        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][0]['name'] == 'article_id'
        assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
            'get']['parameters'][1]['name'] == 'user_id'

    def test_apispec_path_summary_auto_generation(self):
        app = self.create_app()

        @app.route('/users')
        @response(Schema)
        def get_users():
            pass

        @app.route('/users/<id>', methods=['PUT'])
        @response(Schema)
        def update_user(id):
            pass

        @app.route('/users/<id>', methods=['DELETE'])
        @response(Schema)
        def delete_user(id):
            """
            Summary from Docs

            Delete a user with specified ID.
            """
            pass

        client = app.test_client()

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/users']['get']['summary'] == 'Get Users'
        assert rv.json['paths']['/users/{id}']['put']['summary'] == \
            'Update User'
        assert rv.json['paths']['/users/{id}']['delete']['summary'] == \
            'Summary from Docs'
        assert rv.json['paths']['/users/{id}']['delete']['description'] == \
            'Delete a user with specified ID.'

    def test_route_shortcuts(self):
        app = self.create_app()

        @app.get('/pet')
        @response(Schema)
        def test_get():
            return {'name': 'get'}

        @app.post('/pet')
        @response(Schema)
        def test_post():
            return {'name': 'post'}

        @app.put('/pet')
        @response(Schema)
        def test_put():
            return {'name': 'put'}

        @app.patch('/pet')
        @response(Schema)
        def test_patch():
            return {'name': 'patch'}

        @app.delete('/pet')
        @response(Schema)
        def test_delete():
            return {'name': 'delete'}

        client = app.test_client()
        rv = client.get('/pet')
        assert rv.json['name'] == 'get'

        rv = client.post('/pet')
        assert rv.json['name'] == 'post'

        rv = client.put('/pet')
        assert rv.json['name'] == 'put'

        rv = client.patch('/pet')
        assert rv.json['name'] == 'patch'

        rv = client.delete('/pet')
        assert rv.json['name'] == 'delete'

        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/pet']['get']['summary'] == 'Test Get'
        assert rv.json['paths']['/pet']['post']['summary'] == 'Test Post'
        assert rv.json['paths']['/pet']['put']['summary'] == 'Test Put'
        assert rv.json['paths']['/pet']['patch']['summary'] == 'Test Patch'
        assert rv.json['paths']['/pet']['delete']['summary'] == 'Test Delete'

    def test_view_function_arguments(self):
        app = self.create_app()

        class QuerySchema(ma.Schema):
            foo = ma.Str(required=True)
            bar = ma.Str(required=True)

        class PetSchema(ma.Schema):
            name = ma.Str(required=True)
            age = ma.Integer(default=123)

        @app.post('/pets/<int:pet_id>/toys/<int:toy_id>')
        @arguments(QuerySchema)
        @body(PetSchema)
        def test_args(pet_id, toy_id, args, body):
            return {'pet_id': pet_id, 'toy_id': toy_id,
                    'foo': args['foo'], 'bar': args['bar'], **body}

        client = app.test_client()
        rv = client.post('/pets/1/toys/3?foo=yes&bar=no',
                         json={'name': 'dodge', 'age': 5})
        assert rv.status_code == 200
        assert rv.json['pet_id'] == 1
        assert rv.json['toy_id'] == 3
        assert rv.json['foo'] == 'yes'
        assert rv.json['bar'] == 'no'
        assert rv.json['name'] == 'dodge'
        assert rv.json['age'] == 5

    def test_default_openapi_response(self):
        app = self.create_app()

        @app.get('/foo')
        @body(Schema)
        def only_body_schema():
            pass

        @app.get('/bar')
        def no_schema():
            pass

        client = app.test_client()
        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert '204' in rv.json['paths']['/foo']['get']['responses']
        assert '200' in rv.json['paths']['/bar']['get']['responses']
        assert rv.json['paths']['/foo']['get']['responses'][
            '204']['description'] == 'Empty response'
        assert rv.json['paths']['/bar']['get']['responses'][
            '200']['description'] == 'Successful response'

    def test_default_openapi_response_description(self):
        app = self.create_app()
        app.config['200_RESPONSE_DESCRIPTION'] = 'It works'
        app.config['204_RESPONSE_DESCRIPTION'] = 'Nothing'

        @app.get('/foo')
        @body(Schema)
        def only_body_schema():
            pass

        @app.get('/bar')
        def no_schema():
            pass

        client = app.test_client()
        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/foo']['get']['responses'][
            '204']['description'] == 'Nothing'
        assert rv.json['paths']['/bar']['get']['responses'][
            '200']['description'] == 'It works'

    def test_register_validation_error_response(self):
        app = self.create_app()
        error_code = str(app.config['VALIDATION_ERROR_CODE'])

        @app.post('/foo')
        @body(Schema)
        def foo():
            pass

        @app.get('/bar')
        @arguments(Schema)
        def bar():
            pass

        client = app.test_client()
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

    def test_validation_error_config(self):
        app = self.create_app()
        app.config['VALIDATION_ERROR_CODE'] = 422
        app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Bad'

        @app.post('/foo')
        @body(Schema)
        def foo():
            pass

        client = app.test_client()
        rv = client.get('/openapi.json')
        assert rv.status_code == 200
        validate_spec(rv.json)
        assert rv.json['paths']['/foo']['post']['responses']['422'] is not None
        assert rv.json['paths']['/foo']['post']['responses'][
            '422']['description'] == 'Bad'
