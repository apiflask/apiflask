import pytest
from openapi_spec_validator import validate_spec

from apiflask import output

from .schemas import FooSchema


def test_async_view(app, client):
    if not hasattr(app, 'ensure_sync'):
        pytest.skip('This test requires Flask 2.0 or higher')

    @app.get('/')
    async def index():
        return {'message': 'hello'}

    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json['message'] == 'hello'


def test_output_on_async_view(app, client):
    if not hasattr(app, 'ensure_sync'):
        pytest.skip('This test requires Flask 2.0 or higher')

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
