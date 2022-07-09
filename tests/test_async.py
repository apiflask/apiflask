import pytest
from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from apiflask import HTTPTokenAuth


@pytest.fixture(autouse=True)
def skip_async_test(app):
    if not hasattr(app, 'ensure_sync'):
        pytest.skip('This test requires Flask 2.0 or higher')


def test_async_view(app, client):

    @app.get('/')
    async def index():
        return {'message': 'hello'}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json['message'] == 'hello'


def test_async_error_processor(app, client):

    @app.error_processor
    async def custom_error_processor(e):
        return {'foo': 'test'}, e.status_code, e.headers

    rv = client.get('/foo')
    assert rv.status_code == 404
    assert rv.json['foo'] == 'test'


def test_async_spec_processor(app, client):

    @app.spec_processor
    async def update_spec(spec):
        spec['info']['title'] = 'Updated Title'
        return spec

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['info']['title'] == 'Updated Title'


def test_auth_required_on_async_view(app, client):
    auth = HTTPTokenAuth()

    @app.get('/')
    @app.auth_required(auth)
    async def index():
        pass

    rv = client.get('/')
    assert rv.status_code == 401


def test_doc_on_async_view(app, client):

    @app.get('/')
    @app.doc(summary='Test Root Endpoint')
    async def index():
        return {'echo': 1234}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json['echo'] == 1234


def test_input_on_async_view(app, client):

    @app.post('/')
    @app.input(FooSchema)
    async def index(data):
        return data

    data = {'id': 1, 'name': 'foo'}
    rv = client.post('/', json=data)
    assert rv.status_code == 200
    assert rv.json == data


def test_output_on_async_view(app, client):

    @app.get('/foo')
    @app.output(FooSchema)
    async def foo():
        return {'id': 1, 'name': 'foo'}

    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json['id'] == 1
    assert rv.json['name'] == 'foo'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['responses']['200']
    assert rv.json['paths']['/foo']['get']['responses']['200'][
        'content']['application/json']['schema']['$ref'] == '#/components/schemas/Foo'


def test_async_doc_input_and_output_decorator(app, client):

    @app.post('/')
    @app.doc(summary='Test Root Endpoint')
    @app.input(FooSchema)
    @app.output(FooSchema)
    async def index(data):
        return data

    payload = {'id': 1, 'name': 'foo'}
    rv = client.post('/', json=payload)
    assert rv.status_code == 200
    assert rv.json == payload
