from flask_httpauth import HTTPBasicAuth
from openapi_spec_validator import validate_spec

from apiflask import input, output, auth_required, doc
from .schemas import FooSchema, BarSchema, BazSchema, QuerySchema, \
    PaginationSchema, HeaderSchema


def test_apispec(app, client):

    auth = HTTPBasicAuth()

    @app.apispec_processor
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
    @auth_required(auth)
    @input(QuerySchema, location='query')
    @input(FooSchema)
    @output(FooSchema)
    @doc(responses={404: 'foo not found'})
    def foo():
        return {'id': 123, 'name': auth.current_user()['user']}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert app.title == 'Foo'
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


def test_apispec_schemas(app, client):

    @app.route('/foo')
    @output(FooSchema(partial=True))
    def foo():
        pass

    @app.route('/bar')
    @output(BarSchema(many=True))
    def bar():
        pass

    @app.route('/baz')
    @output(BazSchema)
    def baz():
        pass

    with app.app_context():
        apispec = app.apispec
    assert len(apispec['components']['schemas']) == 3
    assert 'FooUpdate' in apispec['components']['schemas']
    assert 'BarList' in apispec['components']['schemas']
    assert 'Baz' in apispec['components']['schemas']


def test_apispec_path_summary_description_from_docs(app, client):

    @app.route('/users')
    @output(FooSchema)
    def get_users():
        """Get Users"""
        pass

    @app.route('/users/<id>', methods=['PUT'])
    @output(FooSchema)
    def update_user(id):
        """
        Update User

        Update a user with specified ID.
        """
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/users']['get']['summary'] == 'Get Users'
    assert rv.json['paths']['/users/{id}']['put']['summary'] == \
        'Update User'
    assert rv.json['paths']['/users/{id}']['put']['description'] == \
        'Update a user with specified ID.'


def test_apispec_path_parameters_registration(app, client):

    @app.route('/strings/<some_string>')
    @output(FooSchema)
    def get_string(some_string):
        pass

    @app.route('/floats/<float:some_float>', methods=['POST'])
    @output(FooSchema)
    def get_float(some_float):
        pass

    @app.route('/integers/<int:some_integer>', methods=['PUT'])
    @output(FooSchema)
    def get_integer(some_integer):
        pass

    @app.route('/users/<int:user_id>/articles/<int:article_id>')
    @output(FooSchema)
    def get_article(user_id, article_id):
        pass

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
        'get']['parameters'][0]['name'] == 'user_id'
    assert rv.json['paths']['/users/{user_id}/articles/{article_id}'][
        'get']['parameters'][1]['name'] == 'article_id'


def test_apispec_path_summary_auto_generation(app, client):

    @app.route('/users')
    @output(FooSchema)
    def get_users():
        pass

    @app.route('/users/<id>', methods=['PUT'])
    @output(FooSchema)
    def update_user(id):
        pass

    @app.route('/users/<id>', methods=['DELETE'])
    @output(FooSchema)
    def delete_user(id):
        """
        Summary from Docs

        Delete a user with specified ID.
        """
        pass

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


def test_default_openapi_response(app, client):

    @app.get('/foo')
    @input(FooSchema)
    def only_body_schema():
        pass

    @app.get('/bar')
    def no_schema():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '204' in rv.json['paths']['/foo']['get']['responses']
    assert '200' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '204']['description'] == 'Empty response'
    assert rv.json['paths']['/bar']['get']['responses'][
        '200']['description'] == 'Successful response'


def test_default_openapi_response_description(app, client):

    app.config['200_DESCRIPTION'] = 'It works'
    app.config['204_DESCRIPTION'] = 'Nothing'

    @app.get('/foo')
    @input(FooSchema)
    def only_body_schema(foo):
        pass

    @app.get('/bar')
    def no_schema():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses'][
        '204']['description'] == 'Nothing'
    assert rv.json['paths']['/bar']['get']['responses'][
        '200']['description'] == 'It works'


def test_path_arguments_detection(app, client):

    @app.route('/foo/<bar>')
    @output(FooSchema)
    def pattern1(bar):
        pass

    @app.route('/<foo>/bar')
    @output(FooSchema)
    def pattern2(foo):
        pass

    @app.route('/<int:foo>/<bar>/baz')
    @output(FooSchema)
    def pattern3(foo, bar):
        pass

    @app.route('/foo/<int:bar>/<int:baz>')
    @output(FooSchema)
    def pattern4(bar, baz):
        pass

    @app.route('/<int:foo>/<bar>/<float:baz>')
    @output(FooSchema)
    def pattern5(foo, bar, baz):
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/foo/{bar}' in rv.json['paths']
    assert '/{foo}/bar' in rv.json['paths']
    assert '/{foo}/{bar}/baz' in rv.json['paths']
    assert '/foo/{bar}/{baz}' in rv.json['paths']
    assert '/{foo}/{bar}/{baz}' in rv.json['paths']
    assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
        'parameters'][0]['schema']['type'] == 'integer'
    assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
        'parameters'][1]['schema']['type'] == 'string'
    assert rv.json['paths']['/{foo}/{bar}/{baz}']['get'][
        'parameters'][2]['schema']['type'] == 'number'


def test_path_arguments_order(app, client):

    @app.route('/<foo>/bar')
    @input(QuerySchema, 'query')
    @output(FooSchema)
    def path_and_query(foo, query):
        pass

    @app.route('/<foo>/<bar>')
    @output(FooSchema)
    def two_path_variables(foo, bar):
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/{foo}/bar' in rv.json['paths']
    assert '/{foo}/{bar}' in rv.json['paths']
    assert rv.json['paths']['/{foo}/bar']['get'][
        'parameters'][0]['name'] == 'foo'
    assert rv.json['paths']['/{foo}/bar']['get'][
        'parameters'][1]['name'] == 'id'
    assert rv.json['paths']['/{foo}/{bar}']['get'][
        'parameters'][0]['name'] == 'foo'
    assert rv.json['paths']['/{foo}/{bar}']['get'][
        'parameters'][1]['name'] == 'bar'


def test_query_arguments(app, client):

    @app.route('/foo')
    @input(QuerySchema, 'query')
    @output(FooSchema)
    def foo(query):
        pass

    @app.route('/bar')
    @input(QuerySchema, 'query')
    @input(PaginationSchema, 'query')
    @input(HeaderSchema, 'headers')
    def bar(query, pagination, header):
        return {
            'query': query['id'],
            'pagination': pagination,
            'foo': header['foo']
        }

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/foo' in rv.json['paths']
    assert '/bar' in rv.json['paths']
    assert rv.json['paths']['/foo']['get'][
        'parameters'][0]['name'] == 'id'
    assert len(rv.json['paths']['/foo']['get']['parameters']) == 1
    assert len(rv.json['paths']['/bar']['get']['parameters']) == 3
    rv = client.get('/bar')
    assert rv.status_code == 200
    assert rv.json['query'] == 1
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10
    assert rv.json['foo'] == 'bar'
