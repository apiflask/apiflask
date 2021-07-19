import pytest
from openapi_spec_validator import validate_spec

from .schemas import FooSchema
from apiflask import output


def skip_flask1(app):
    if not hasattr(app, 'ensure_sync'):
        pytest.skip('This test requires Flask 2.0 or higher')


def test_async_view(app, client):
    skip_flask1(app)

    @app.get('/')
    async def index():
        return {'message': 'hello'}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json['message'] == 'hello'


def test_output_on_async_view(app, client):
    skip_flask1(app)

    @app.get('/foo')
    @output(FooSchema)
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


def test_async_error_processor(app, client):
    skip_flask1(app)

    @app.error_processor
    async def custom_error_processor(e):
        return {'foo': 'test'}, e.status_code, e.headers

    rv = client.get('/foo')
    assert rv.status_code == 404
    assert rv.json['foo'] == 'test'


def test_async_spec_processor(app, client):
    skip_flask1(app)

    @app.spec_processor
    async def update_spec(spec):
        spec['info']['title'] = 'Updated Title'
        return spec

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['info']['title'] == 'Updated Title'
