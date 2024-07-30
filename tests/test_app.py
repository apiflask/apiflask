import openapi_spec_validator as osv
import pytest
from apispec import BasePlugin
from flask import Blueprint
from flask.views import MethodView

from .schemas import Bar
from .schemas import Foo
from .schemas import Pagination
from apiflask import APIBlueprint
from apiflask import APIFlask
from apiflask import Schema
from apiflask.exceptions import abort
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
    assert rv.json['message'] == 'Not Found'
    assert rv.json['detail'] == {}

    app = APIFlask(__name__, json_errors=False)
    assert app.json_errors is False
    rv = app.test_client().get('/not-exist')
    assert rv.status_code == 404
    assert rv.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'!doctype' in rv.data.lower()


def test_json_errors_reuse_werkzeug_headers(app, client):
    # test automatic 405
    @app.get('/foo')
    def foo():
        pass

    # test manually raise 405
    @app.get('/bar')
    def bar():
        from werkzeug.exceptions import MethodNotAllowed

        raise MethodNotAllowed(valid_methods=['GET'])

    rv = client.post('/foo')
    assert rv.status_code == 405
    assert 'Allow' in rv.headers

    rv = client.get('/bar')
    assert rv.status_code == 405
    assert rv.headers['Content-Type'] == 'application/json'
    assert rv.headers['Allow'] == 'GET'


def test_view_function_arguments_order(app, client):
    class Query(Schema):
        foo = String(required=True)
        bar = String(required=True)

    class Pet(Schema):
        name = String(required=True)
        age = Integer(dump_default=123)

    @app.post('/pets/<int:pet_id>/toys/<int:toy_id>')
    @app.input(Query, location='query', arg_name='query')
    @app.input(Pagination, location='query', arg_name='pagination')
    @app.input(Pet, location='json')
    def pets(pet_id, toy_id, query, pagination, json_data):
        return {
            'pet_id': pet_id,
            'toy_id': toy_id,
            'foo': query['foo'],
            'bar': query['bar'],
            'pagination': pagination,
            **json_data,
        }

    @app.route('/animals/<int:pet_id>/toys/<int:toy_id>')
    class Animals(MethodView):
        @app.input(Query, location='query', arg_name='query')
        @app.input(Pagination, location='query', arg_name='pagination')
        @app.input(Pet, location='json')
        def post(self, pet_id, toy_id, query, pagination, json_data):
            return {
                'pet_id': pet_id,
                'toy_id': toy_id,
                'foo': query['foo'],
                'bar': query['bar'],
                'pagination': pagination,
                **json_data,
            }

    rv = client.post('/pets/1/toys/3?foo=yes&bar=no', json={'name': 'dodge', 'age': 5})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 1
    assert rv.json['toy_id'] == 3
    assert rv.json['foo'] == 'yes'
    assert rv.json['bar'] == 'no'
    assert rv.json['name'] == 'dodge'
    assert rv.json['age'] == 5
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10

    rv = client.post('/animals/1/toys/3?foo=yes&bar=no', json={'name': 'dodge', 'age': 5})
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


def test_apply_custom_error_callback_for_generic_errors():
    app = APIFlask(__name__, json_errors=False)
    client = app.test_client()

    @app.error_processor
    def custom_error_handler(e):
        return {'message': 'custom handler'}, e.status_code

    rv = client.get('/not-exist')
    assert rv.status_code == 404
    assert 'message' in rv.json
    assert rv.json['message'] == 'custom handler'


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
    osv.validate(rv.json)
    assert rv.json['tags'] == [{'name': 'test'}]
    assert '/foo' not in rv.json['paths']
    assert '/bar' not in rv.json['paths']
    assert '/baz' in rv.json['paths']
    assert '/spam' in rv.json['paths']


def test_dispatch_static_request(app, client):
    # positional arguments
    @app.get('/mystatic/<int:pet_id>')
    @app.input(Foo)
    def mystatic(pet_id, json_data):  # endpoint: mystatic
        return {'pet_id': pet_id, 'foo': json_data}

    # positional arguments
    # blueprint static route accepts both keyword/positional arguments
    bp = APIBlueprint('foo', __name__, static_folder='static')
    app.register_blueprint(bp, url_prefix='/foo')

    rv = client.get('/mystatic/2', json={'id': 1, 'name': 'foo'})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 2
    assert rv.json['foo'] == {'id': 1, 'name': 'foo'}

    rv = client.get('/foo/static/hello.css')  # endpoint: foo.static
    assert rv.status_code == 404

    # keyword arguments
    rv = client.get('/static/hello.css')  # endpoint: static
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


@pytest.mark.parametrize(
    'resolver', [APIFlask._schema_name_resolver, schema_name_resolver1, schema_name_resolver2]
)
def test_schema_name_resolver(app, client, resolver):
    app.schema_name_resolver = resolver

    @app.route('/foo')
    @app.output(Foo)
    def foo():
        pass

    @app.route('/bar')
    @app.output(Bar(partial=True))
    def bar():
        pass

    spec = app.spec
    if resolver == schema_name_resolver1:
        assert 'Foo' in spec['components']['schemas']
        assert 'Bar_' in spec['components']['schemas']
    elif resolver == schema_name_resolver2:
        assert 'Foo' in spec['components']['schemas']
        assert 'BarPartial' in spec['components']['schemas']
    else:
        assert 'Foo' in spec['components']['schemas']
        assert 'BarUpdate' in spec['components']['schemas']


@pytest.mark.parametrize('ui_name', ['swagger-ui', 'redoc', 'elements', 'rapidoc', 'rapipdf'])
def test_docs_ui(ui_name):
    app = APIFlask(__name__, docs_ui=ui_name)
    client = app.test_client()

    rv = client.get('/docs')
    assert rv.status_code == 200


def test_bad_docs_ui():
    with pytest.raises(ValueError):
        APIFlask(__name__, docs_ui='bad')


def test_return_list_as_json(app, client):
    test_list = ['foo', 'bar', 'baz']

    @app.get('/single')
    def single_value():
        return test_list

    @app.get('/multi')
    def multi_values():
        return test_list, 201, {'X-Foo': 'bar'}

    rv = client.get('/single')
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == 'application/json'
    assert rv.json == test_list

    rv = client.get('/multi')
    assert rv.status_code == 201
    assert rv.headers['Content-Type'] == 'application/json'
    assert rv.json == test_list


def test_apispec_plugins(app):
    class TestPlugin(BasePlugin):
        def operation_helper(self, path=None, operations=None, **kwargs) -> None:
            operations.update({'post': 'some_injected_test_data'})

    app.spec_plugins = [TestPlugin()]

    @app.get('/plugin_test')
    def single_value():
        return 'plugin_test'

    spec = app._get_spec('json')

    assert spec['paths']['/plugin_test'].get('post') == 'some_injected_test_data'


def test_spec_decorators(app, client):
    def auth_decorator(f):
        def wrapper(*args, **kwargs):
            abort(401)
            return f(*args, **kwargs)

        return wrapper

    app.config['SPEC_DECORATORS'] = [auth_decorator]

    rv = client.get('/openapi.json')
    assert rv.status_code == 401

    rv = client.get('/docs')
    assert rv.status_code == 200


def test_docs_decorators(app, client):
    def auth_decorator(f):
        def wrapper(*args, **kwargs):
            abort(401)
            return f(*args, **kwargs)

        return wrapper

    app.config['DOCS_DECORATORS'] = [auth_decorator]

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    rv = client.get('/docs')
    assert rv.status_code == 401


def test_swagger_ui_oauth_redirect_decorators(app, client):
    def auth_decorator(f):
        def wrapper(*args, **kwargs):
            abort(401)
            return f(*args, **kwargs)

        return wrapper

    app.config['SWAGGER_UI_OAUTH_REDIRECT_DECORATORS'] = [auth_decorator]

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    rv = client.get('/docs')
    assert rv.status_code == 200

    rv = client.get('/docs/oauth2-redirect')
    assert rv.status_code == 401
