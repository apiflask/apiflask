import pytest
from openapi_spec_validator import validate_spec

from apiflask import output

from .schemas import FooSchema


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
