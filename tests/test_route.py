import pytest
from flask.views import MethodView
from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from apiflask import APIBlueprint
from apiflask import auth_required
from apiflask import doc
from apiflask import HTTPTokenAuth
from apiflask import output


@pytest.mark.parametrize('method', ['get', 'post', 'put', 'patch', 'delete'])
def test_route_shortcuts(app, client, method):
    route_method = getattr(app, method)
    client_method = getattr(client, method)

    @route_method('/pet')
    @output(FooSchema)
    def test_shortcuts():
        return {'name': method}

    assert client_method('/pet').json['name'] == method

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/pet'][method]


def test_route_on_method_view(app, client):
    @app.route('/')
    class Foo(MethodView):
        def get(self):
            return 'get'

        def post(self):
            return 'post'

        def delete(self):
            return 'delete'

        def put(self):
            return 'put'

        def patch(self):
            return 'patch'

    rv = client.get('/')
    assert rv.data == b'get'
    rv = client.post('/')
    assert rv.data == b'post'
    rv = client.delete('/')
    assert rv.data == b'delete'
    rv = client.put('/')
    assert rv.data == b'put'
    rv = client.patch('/')
    assert rv.data == b'patch'


def test_blueprint_route_on_method_view(app, client):
    bp = APIBlueprint('test', __name__, tag='foo')

    @bp.route('/')
    class Foo(MethodView):
        def get(self):
            return 'get'

        def post(self):
            return 'post'

        def delete(self):
            return 'delete'

        def put(self):
            return 'put'

        def patch(self):
            return 'patch'

    app.register_blueprint(bp)

    rv = client.get('/')
    assert rv.data == b'get'
    rv = client.post('/')
    assert rv.data == b'post'
    rv = client.delete('/')
    assert rv.data == b'delete'
    rv = client.put('/')
    assert rv.data == b'put'
    rv = client.patch('/')
    assert rv.data == b'patch'


def test_bad_route_decorator_usages(app):
    with pytest.raises(RuntimeError):
        @app.get('/foo', methods=['GET'])
        def foo(self):
            pass

    with pytest.raises(RuntimeError):
        @app.get('/baz')
        class Baz(MethodView):
            def get(self):
                pass


def test_class_attribute_decorators(app, client):
    auth = HTTPTokenAuth()

    @app.route('/')
    class Foo(MethodView):
        decorators = [auth_required(auth), doc(responses=[404])]

        def get(self):
            pass

        def post(self):
            pass

    rv = client.get('/')
    assert rv.status_code == 401
    rv = client.post('/')
    assert rv.status_code == 401

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '404' in rv.json['paths']['/']['get']['responses']
    assert '404' in rv.json['paths']['/']['post']['responses']
    assert 'BearerAuth' in rv.json['paths']['/']['get']['security'][0]
    assert 'BearerAuth' in rv.json['paths']['/']['post']['security'][0]


def test_overwrite_class_attribute_decorators(app, client):
    @app.route('/')
    class Foo(MethodView):
        decorators = [doc(deprecated=True, tag='foo')]

        def get(self):
            pass

        @doc(deprecated=False)
        def post(self):
            pass

        @doc(tag='bar')
        def delete(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/']['get']['deprecated']
    assert rv.json['paths']['/']['get']['tags'] == ['foo']
    assert rv.json['paths']['/']['post']['tags'] == ['foo']
    assert rv.json['paths']['/']['delete']['tags'] == ['bar']
    assert 'deprecated' not in rv.json['paths']['/']['post']
