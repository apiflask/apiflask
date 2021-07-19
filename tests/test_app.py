import pytest
from flask import Blueprint
from flask.views import MethodView
from openapi_spec_validator import validate_spec

from .schemas import BarSchema
from .schemas import FooSchema
from .schemas import PaginationSchema
from apiflask import APIBlueprint
from apiflask import APIFlask
from apiflask import input
from apiflask import output
from apiflask import Schema
from apiflask.fields import Integer
from apiflask.fields import String


def test_app_init(app):
    assert app
    assert hasattr(app, 'import_name')
    assert hasattr(app, 'title')
    assert 'TAGS' in app.config
    assert 'openapi' in app.blueprints


def test_json_errors(app, client):
    assert app.json_errors is True

    rv = client.get('/not-exist')
    assert rv.status_code == 404
    assert rv.headers['Content-Type'] == 'application/json'
    assert 'message' in rv.json
    assert 'detail' in rv.json
    assert rv.json['status_code'] == 404

    app = APIFlask(__name__, json_errors=False)
    assert app.json_errors is False
    rv = app.test_client().get('/not-exist')
    assert rv.status_code == 404
    assert rv.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'!DOCTYPE' in rv.data


def test_view_function_arguments_order(app, client):

    class QuerySchema(Schema):
        foo = String(required=True)
        bar = String(required=True)

    class PetSchema(Schema):
        name = String(required=True)
        age = Integer(default=123)

    @app.post('/pets/<int:pet_id>/toys/<int:toy_id>')
    @input(QuerySchema, 'query')
    @input(PaginationSchema, 'query')
    @input(PetSchema)
    def pets(pet_id, toy_id, query, pagination, body):
        return {'pet_id': pet_id, 'toy_id': toy_id,
                'foo': query['foo'], 'bar': query['bar'], 'pagination': pagination, **body}

    @app.route('/animals/<int:pet_id>/toys/<int:toy_id>')
    class Animals(MethodView):
        @input(QuerySchema, 'query')
        @input(PaginationSchema, 'query')
        @input(PetSchema)
        def post(self, pet_id, toy_id, query, pagination, body):
            return {'pet_id': pet_id, 'toy_id': toy_id,
                    'foo': query['foo'], 'bar': query['bar'], 'pagination': pagination, **body}

    rv = client.post('/pets/1/toys/3?foo=yes&bar=no',
                     json={'name': 'dodge', 'age': 5})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 1
    assert rv.json['toy_id'] == 3
    assert rv.json['foo'] == 'yes'
    assert rv.json['bar'] == 'no'
    assert rv.json['name'] == 'dodge'
    assert rv.json['age'] == 5
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10

    rv = client.post('/animals/1/toys/3?foo=yes&bar=no',
                     json={'name': 'dodge', 'age': 5})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 1
    assert rv.json['toy_id'] == 3
    assert rv.json['foo'] == 'yes'
    assert rv.json['bar'] == 'no'
    assert rv.json['name'] == 'dodge'
    assert rv.json['age'] == 5
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10


def test_error_callback(app, client):
    @app.error_processor
    def custom_error_handler(e):
        assert e.status_code == 500
        assert e.detail == {}
        assert e.headers == {}
        assert e.message == 'Internal Server Error'
        return {'message': 'something was wrong'}, 200

    @app.get('/')
    def error():
        print(a)  # noqa: F821
        return ''

    rv = client.get('/not-exist')
    assert rv.status_code == 200
    assert 'message' in rv.json
    assert rv.json['message'] == 'something was wrong'

    rv = client.get('/')
    assert rv.status_code == 200
    assert 'message' in rv.json
    assert rv.json['message'] == 'something was wrong'


def test_skip_raw_blueprint(app, client):
    raw_bp = Blueprint('raw', __name__)
    api_bp = APIBlueprint('api', __name__, tag='test')

    @raw_bp.route('/foo')
    def foo():
        pass

    @raw_bp.route('/bar')
    class Bar(MethodView):
        def get(self):
            pass

    @api_bp.get('/baz')
    def baz():
        pass

    @api_bp.route('/spam')
    class Spam(MethodView):
        def get(self):
            pass

    app.register_blueprint(raw_bp)
    app.register_blueprint(api_bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == [{'name': 'test'}]
    assert '/foo' not in rv.json['paths']
    assert '/bar' not in rv.json['paths']
    assert '/baz' in rv.json['paths']
    assert '/spam' in rv.json['paths']


def test_dispatch_static_request(app, client):
    # keyword arguments
    rv = client.get('/static/hello.css')  # endpoint: static
    assert rv.status_code == 404

    # positional arguments
    @app.get('/mystatic/<int:pet_id>')
    @input(FooSchema)
    def mystatic(pet_id, foo):  # endpoint: mystatic
        return {'pet_id': pet_id, 'foo': foo}

    rv = client.get('/mystatic/2', json={'id': 1, 'name': 'foo'})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 2
    assert rv.json['foo'] == {'id': 1, 'name': 'foo'}

    # positional arguments
    # blueprint static route accepts both keyword/positional arguments
    bp = APIBlueprint('foo', __name__, static_folder='static')
    app.register_blueprint(bp, url_prefix='/foo')
    rv = client.get('/foo/static/hello.css')  # endpoint: foo.static
    assert rv.status_code == 404


def schema_name_resolver1(schema):
    name = schema.__class__.__name__
    if schema.partial:
        name += '_'
    return name


def schema_name_resolver2(schema):
    name = schema.__class__.__name__
    if name.endswith('Schema'):
        name = name[:-6] or name
    if schema.partial:
        name += 'Partial'
    return name


@pytest.mark.parametrize('resolver', [
    APIFlask._schema_name_resolver,
    schema_name_resolver1,
    schema_name_resolver2
])
def test_schema_name_resolver(app, client, resolver):
    app.schema_name_resolver = resolver

    @app.route('/foo')
    @output(FooSchema)
    def foo():
        pass

    @app.route('/bar')
    @output(BarSchema(partial=True))
    def bar():
        pass

    spec = app.spec
    if resolver == schema_name_resolver1:
        assert 'FooSchema' in spec['components']['schemas']
        assert 'BarSchema_' in spec['components']['schemas']
    elif resolver == schema_name_resolver2:
        assert 'Foo' in spec['components']['schemas']
        assert 'BarPartial' in spec['components']['schemas']
    else:
        assert 'Foo' in spec['components']['schemas']
        assert 'BarUpdate' in spec['components']['schemas']
