import pytest
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint
from apiflask import input
from apiflask import output
from apiflask import auth_required
from apiflask import doc
from apiflask.security import HTTPBasicAuth
from apiflask.security import HTTPTokenAuth
from apiflask.fields import String

from .schemas import FooSchema
from .schemas import BarSchema
from .schemas import QuerySchema


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
    @app.post('/foo')
    @input(FooSchema, example=['foo', 'bar', 'baz'])
    def foo():
        pass

    @app.post('/bar')
    @input(FooSchema, example={'name': 'foo', 'age': 20})
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['post']['requestBody'][
        'content']['application/json']['example'] == ['foo', 'bar', 'baz']
    assert rv.json['paths']['/bar']['post']['requestBody'][
        'content']['application/json']['example'] == {'name': 'foo', 'age': 20}


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
    @app.get('/foo')
    @output(FooSchema, example=['foo', 'bar', 'baz'])
    def foo():
        pass

    @app.get('/bar')
    @output(FooSchema, example={'name': 'foo', 'age': 20})
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['200'][
        'content']['application/json']['example'] == ['foo', 'bar', 'baz']
    assert rv.json['paths']['/bar']['get']['responses']['200'][
        'content']['application/json']['example'] == {'name': 'foo', 'age': 20}


def test_output_with_empty_dict_as_schema(app, client):
    @app.delete('/foo')
    @output({}, 204)
    def delete_foo():
        return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'content' not in rv.json['paths']['/foo']['delete']['responses']['204']

    rv = client.delete('/foo')
    assert rv.status_code == 204


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
    @doc(tag='foo')
    def foo():
        pass

    @app.route('/bar')
    @doc(tag=['foo', 'bar'])
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
    @input(FooSchema)
    @output(FooSchema)
    @doc(responses={200: 'success', 400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    @app.route('/bar')
    @input(FooSchema)
    @output(FooSchema)
    @doc(responses=[200, 400, 404, 500])
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '200' in rv.json['paths']['/foo']['get']['responses']
    assert '400' in rv.json['paths']['/foo']['get']['responses']
    # don't overwrite exist error description
    assert rv.json['paths']['/foo']['get']['responses'][
        '200']['description'] == 'Successful response'
    assert rv.json['paths']['/foo']['get']['responses'][
        '400']['description'] == 'Validation error'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '404']['description'] == 'not found'
    assert '500' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '500']['description'] == 'server error'

    assert '200' in rv.json['paths']['/bar']['get']['responses']
    assert '400' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '200']['description'] == 'Successful response'
    assert rv.json['paths']['/bar']['get']['responses'][
        '400']['description'] == 'Validation error'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '404']['description'] == 'Not Found'
    assert '500' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '500']['description'] == 'Internal Server Error'
