from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from .schemas import HeaderSchema
from .schemas import PaginationSchema
from .schemas import QuerySchema


def test_spec_path_summary_description_from_docs(app, client):
    @app.route('/users')
    @app.output(FooSchema)
    def get_users():
        """Get Users"""
        pass

    @app.route('/users/<id>', methods=['PUT'])
    @app.output(FooSchema)
    def update_user(id):
        """Update User

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


def test_spec_path_parameters_registration(app, client):
    @app.route('/strings/<some_string>')
    @app.output(FooSchema)
    def get_string(some_string):
        pass

    @app.route('/floats/<float:some_float>', methods=['POST'])
    @app.output(FooSchema)
    def get_float(some_float):
        pass

    @app.route('/integers/<int:some_integer>', methods=['PUT'])
    @app.output(FooSchema)
    def get_integer(some_integer):
        pass

    @app.route('/users/<int:user_id>/articles/<int:article_id>')
    @app.output(FooSchema)
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


def test_spec_path_summary_auto_generation(app, client):
    @app.route('/users')
    @app.output(FooSchema)
    def get_users():
        pass

    @app.route('/users/<id>', methods=['PUT'])
    @app.output(FooSchema)
    def update_user(id):
        pass

    @app.route('/users/<id>', methods=['DELETE'])
    @app.output(FooSchema)
    def delete_user(id):
        """Summary from Docs

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


def test_path_arguments_detection(app, client):
    @app.route('/foo/<bar>')
    @app.output(FooSchema)
    def pattern1(bar):
        pass

    @app.route('/<foo>/bar')
    @app.output(FooSchema)
    def pattern2(foo):
        pass

    @app.route('/<int:foo>/<bar>/baz')
    @app.output(FooSchema)
    def pattern3(foo, bar):
        pass

    @app.route('/foo/<int:bar>/<int:baz>')
    @app.output(FooSchema)
    def pattern4(bar, baz):
        pass

    @app.route('/<int:foo>/<bar>/<float:baz>')
    @app.output(FooSchema)
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
    @app.input(QuerySchema, 'query')
    @app.output(FooSchema)
    def path_and_query(foo, query):
        pass

    @app.route('/<foo>/<bar>')
    @app.output(FooSchema)
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


def test_parameters_registration(app, client):
    @app.route('/foo')
    @app.input(QuerySchema, 'query')
    @app.output(FooSchema)
    def foo(query):
        pass

    @app.route('/bar')
    @app.input(QuerySchema, 'query')
    @app.input(PaginationSchema, 'query')
    @app.input(HeaderSchema, 'headers')
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
    assert len(rv.json['paths']['/bar']['get']['parameters']) == 4
    rv = client.get('/bar')
    assert rv.status_code == 200
    assert rv.json['query'] == 1
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10
    assert rv.json['foo'] == 'bar'


def test_register_validation_error_response(app, client):
    error_code = str(app.config['VALIDATION_ERROR_STATUS_CODE'])

    @app.post('/foo')
    @app.input(FooSchema)
    def foo():
        pass

    @app.get('/bar')
    @app.input(FooSchema, 'query')
    def bar():
        pass

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


def test_auto_404_error(app, client):
    @app.get('/foo')
    def foo():
        pass

    @app.get('/bar/<int:id>')
    def bar():
        pass

    @app.get('/baz/<int:id>')
    @app.doc(responses={404: 'Pet not found'})
    def baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '404' not in rv.json['paths']['/foo']['get']['responses']
    assert '404' in rv.json['paths']['/bar/{id}']['get']['responses']
    assert rv.json['paths']['/bar/{id}']['get']['responses'][
        '404']['description'] == 'Not found'
    assert rv.json['paths']['/baz/{id}']['get']['responses'][
        '404']['description'] == 'Pet not found'
