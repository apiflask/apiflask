import openapi_spec_validator as osv
import pytest

from .schemas import Foo
from .schemas import ResponseHeader
from apiflask.fields import Boolean
from apiflask.fields import Integer
from apiflask.fields import List
from apiflask.fields import Number
from apiflask.fields import String


def test_spec_with_dict_headers(app, client):
    @app.route('/foo')
    @app.output(
        Foo,
        headers={
            'X-boolean': Boolean(metadata={'description': 'A boolean header'}),
            'X-integer': Integer(metadata={'description': 'An integer header'}),
            'X-number': Number(metadata={'description': 'A number header'}),
            'X-string': String(metadata={'description': 'A string header'}),
            'X-array': List(String(), metadata={'description': 'An array header'}),
        },
    )
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.json['paths']['/foo']['get']['responses']['200']['headers'] == {
        'X-boolean': {
            'description': 'A boolean header',
            'required': False,
            'schema': {'type': 'boolean'},
        },
        'X-integer': {
            'description': 'An integer header',
            'required': False,
            'schema': {'type': 'integer'},
        },
        'X-number': {
            'description': 'A number header',
            'required': False,
            'schema': {'type': 'number'},
        },
        'X-string': {
            'description': 'A string header',
            'required': False,
            'schema': {'type': 'string'},
        },
        'X-array': {
            'description': 'An array header',
            'required': False,
            'schema': {'items': {'type': 'string'}, 'type': 'array'},
            'style': 'form',
            'explode': True,
        },
    }


def test_spec_with_empty_headers(app, client):
    @app.route('/foo')
    @app.output(Foo, headers={})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.json['paths']['/foo']['get']['responses']['200']['headers'] == {}


def test_spec_with_schema_headers(app, client):
    @app.route('/foo')
    @app.output(Foo, headers=ResponseHeader)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.json['paths']['/foo']['get']['responses']['200']['headers'] == {
        'X-Token': {
            'description': 'A custom token header',
            'required': True,
            'schema': {'type': 'string'},
        },
    }


@pytest.mark.parametrize('openapi_version', ['3.0.0', '3.1.0'])
def test_spec_validity_with_headers(app, client, openapi_version):
    app.config['OPENAPI_VERSION'] = openapi_version

    @app.route('/foo')
    @app.output(Foo, headers=ResponseHeader)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
