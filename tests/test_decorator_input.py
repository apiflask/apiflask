import io

import pytest
from openapi_spec_validator import validate_spec
from werkzeug.datastructures import FileStorage

from .schemas import Bar
from .schemas import EnumPathParameter
from .schemas import Files
from .schemas import Foo
from .schemas import Form
from .schemas import FormAndFiles
from apiflask.fields import String
from apiflask.views import MethodView


def test_input(app, client):
    @app.route('/foo', methods=['POST'])
    @app.input(Foo)
    def foo(schema):
        return schema

    @app.route('/bar')
    class Bar(MethodView):
        @app.input(Foo)
        def post(self, data):
            return data

    for rule in ['/foo', '/bar']:
        rv = client.post(rule)
        assert rv.status_code == 422
        assert rv.json == {
            'detail': {
                'json': {'name': ['Missing data for required field.']}
            },
            'message': 'Validation error'
        }

        rv = client.post(rule, json={'id': 1})
        assert rv.status_code == 422
        assert rv.json == {
            'detail': {
                'json': {'name': ['Missing data for required field.']}
            },
            'message': 'Validation error'
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
    @app.input(Foo, location='query')
    @app.input(Bar, location='query')
    def foo(schema, schema2):
        return {'name': schema['name'], 'name2': schema2['name2']}

    rv = client.post('/foo')
    assert rv.status_code == 422
    assert rv.json == {
        'detail': {
            'query': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error'
    }

    rv = client.post('/foo?id=1&name=bar')
    assert rv.status_code == 422
    assert rv.json == {
        'detail': {
            'query': {'name2': ['Missing data for required field.']}
        },
        'message': 'Validation error'
    }

    rv = client.post('/foo?id=1&name=bar&id2=2&name2=baz')
    assert rv.status_code == 200
    assert rv.json == {'name': 'bar', 'name2': 'baz'}

    rv = client.post('/foo?name=bar&name2=baz')
    assert rv.status_code == 200
    assert rv.json == {'name': 'bar', 'name2': 'baz'}


def test_input_with_form_location(app, client):
    @app.post('/')
    @app.input(Form, location='form')
    def index(form_data):
        return form_data

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert 'application/x-www-form-urlencoded' in rv.json['paths']['/']['post']['requestBody'][
        'content']
    assert rv.json['paths']['/']['post']['requestBody']['content'][
        'application/x-www-form-urlencoded']['schema']['$ref'] == '#/components/schemas/Form'
    assert 'Form' in rv.json['components']['schemas']

    rv = client.post('/', data={'name': 'foo'})
    assert rv.status_code == 200
    assert rv.json == {'name': 'foo'}


def test_input_with_files_location(app, client):
    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data):
        data = {}
        if 'image' in files_data and isinstance(files_data['image'], FileStorage):
            data['image'] = True
        return data

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    # TODO: Failed validating 'oneOf' in schema
    # https://github.com/p1c2u/openapi-spec-validator/issues/113
    # validate_spec(rv.json)
    assert 'multipart/form-data' in rv.json['paths']['/']['post']['requestBody']['content']
    assert rv.json['paths']['/']['post']['requestBody'][
        'content']['multipart/form-data']['schema']['$ref'] == '#/components/schemas/Files'
    assert 'image' in rv.json['components']['schemas']['Files']['properties']
    assert rv.json['components']['schemas']['Files']['properties']['image']['type'] == 'string'
    assert rv.json['components']['schemas']['Files']['properties']['image']['format'] == 'binary'

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b'test'), 'test.jpg'),
        },
        content_type='multipart/form-data'
    )
    assert rv.status_code == 200
    assert rv.json == {'image': True}


def test_input_with_form_and_files_location(app, client):
    @app.post('/')
    @app.input(FormAndFiles, location='form_and_files')
    def index(form_data):
        data = {}
        if 'name' in form_data:
            data['name'] = True
        if 'image' in form_data and isinstance(form_data['image'], FileStorage):
            data['image'] = True
        return data

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    # TODO: Failed validating 'oneOf' in schema
    # https://github.com/p1c2u/openapi-spec-validator/issues/113
    # validate_spec(rv.json)
    assert 'multipart/form-data' in rv.json['paths']['/']['post']['requestBody']['content']
    assert rv.json['paths']['/']['post']['requestBody'][
        'content']['multipart/form-data']['schema']['$ref'] == '#/components/schemas/FormAndFiles'
    assert 'name' in rv.json['components']['schemas']['FormAndFiles']['properties']
    assert 'image' in rv.json['components']['schemas']['FormAndFiles']['properties']
    assert rv.json['components']['schemas']['FormAndFiles']['properties']['image'][
        'type'] == 'string'
    assert rv.json['components']['schemas']['FormAndFiles']['properties']['image'][
        'format'] == 'binary'

    rv = client.post(
        '/',
        data={'name': 'foo', 'image': (io.BytesIO(b'test'), 'test.jpg')},
        content_type='multipart/form-data'
    )
    assert rv.status_code == 200
    assert rv.json == {'name': True, 'image': True}


def test_input_with_path_location(app, client):
    @app.get('/<image_type>')
    @app.input(EnumPathParameter, location='path')
    def index(image_type, _):
        return {'image_type': image_type}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    # TODO: Failed validating 'oneOf' in schema
    # https://github.com/p1c2u/openapi-spec-validator/issues/113
    # validate_spec(rv.json)
    assert '/{image_type}' in rv.json['paths']
    assert len(rv.json['paths']['/{image_type}']['get']['parameters']) == 1
    assert rv.json['paths']['/{image_type}']['get']['parameters'][0]['in'] == 'path'
    assert rv.json['paths']['/{image_type}']['get']['parameters'][0]['name'] == 'image_type'
    assert rv.json['paths']['/{image_type}']['get']['parameters'][0]['schema'] == {
        'type': 'string',
        'enum': ['jpg', 'png', 'tiff', 'webp'],
    }

    rv = client.get('/png')
    assert rv.status_code == 200
    assert rv.json == {'image_type': 'png'}

    rv = client.get('/gif')
    assert rv.status_code == 422
    assert rv.json['message'] == 'Validation error'
    assert 'path' in rv.json['detail']
    assert 'image_type' in rv.json['detail']['path']
    assert rv.json['detail']['path']['image_type'] == ['Must be one of: jpg, png, tiff, webp.']


@pytest.mark.parametrize('locations', [
    ['files', 'form'],
    ['files', 'json'],
    ['form', 'json'],
    ['form_and_files', 'json'],
    ['form_and_files', 'form'],
    ['form_and_files', 'files'],
    ['json_or_form', 'json'],
    ['json_or_form', 'files'],
    ['json_or_form', 'form'],
    ['json_or_form', 'form_and_files'],
])
def test_multiple_input_body_location(app, locations):
    with pytest.raises(RuntimeError):
        @app.route('/foo')
        @app.input(Foo, locations[0])
        @app.input(Bar, locations[1])
        def foo(query):
            pass


def test_input_with_dict_schema(app, client):
    dict_schema = {
        'name': String(required=True)
    }

    @app.get('/foo')
    @app.input(dict_schema, 'query')
    def foo(query):
        return query

    @app.post('/bar')
    @app.input(dict_schema, schema_name='MyName')
    def bar(body):
        return body

    @app.post('/baz')
    @app.input(dict_schema)
    def baz(body):
        return body

    @app.post('/spam')
    @app.input(dict_schema)
    def spam(body):
        return body

    rv = client.get('/foo')
    assert rv.status_code == 422
    assert rv.json == {
        'detail': {
            'query': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error'
    }

    rv = client.get('/foo?name=grey')
    assert rv.status_code == 200
    assert rv.json == {'name': 'grey'}

    rv = client.post('/bar')
    assert rv.status_code == 422
    assert rv.json == {
        'detail': {
            'json': {'name': ['Missing data for required field.']}
        },
        'message': 'Validation error'
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
    # https://github.com/p1c2u/openapi-spec-validator/issues/53
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
    @app.input(Foo, example=example)
    def foo():
        pass

    @app.post('/bar')
    @app.input(Foo, examples=examples)
    def bar():
        pass

    @app.route('/baz')
    class Baz(MethodView):
        @app.input(Foo, example=example)
        def get(self):
            pass

        @app.input(Foo, examples=examples)
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
