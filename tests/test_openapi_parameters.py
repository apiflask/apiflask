import openapi_spec_validator as osv
import pytest

from .schemas import DelimitedListQuery
from .schemas import NullableFieldSchema


def test_query_delimited_list_support(app, client):
    @app.route('/users')
    @app.input(DelimitedListQuery, location='query')
    def get_users(query_data):
        """Get Users"""
        return query_data['tags']

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert rv.json['paths']['/users']['get']['parameters'][0]['name'] == 'tags'
    assert rv.json['paths']['/users']['get']['parameters'][0]['style'] == 'form'
    assert rv.json['paths']['/users']['get']['parameters'][0]['explode'] is False

    rv = client.get('/users?tags=admin,editor,user')
    assert rv.status_code == 200
    assert rv.json == ['admin', 'editor', 'user']


@pytest.mark.parametrize('openapi_version', ['3.0.0', '3.1.0'])
@pytest.mark.parametrize(
    'location, expected_in',
    [('query', 'query'), ('headers', 'header'), ('cookies', 'cookie')],
)
def test_nullable_input_field_with_openapi_version(
    app, client, openapi_version, location, expected_in
):
    app.config['OPENAPI_VERSION'] = openapi_version

    @app.get('/foo')
    @app.input(NullableFieldSchema, location=location)
    def foo(**kwargs):
        return {}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)

    assert len(rv.json['paths']['/foo']['get']['parameters']) == 1
    parameters = rv.json['paths']['/foo']['get']['parameters'][0]
    assert parameters['name'] == 'name'
    assert parameters['in'] == expected_in
    expected = (
        {'nullable': True, 'type': 'string'}
        if openapi_version == '3.0.0'
        else {'type': ['string', 'null']}
    )
    assert parameters['schema'] == expected


def test_spec_valid_after_openapi_version_update(app):
    @app.get('/foo')
    @app.input(NullableFieldSchema, location='query')
    def foo(**kwargs):
        return {}

    app.config['OPENAPI_VERSION'] = '3.1.0'
    spec = app.spec
    osv.validate(spec)
    assert spec['openapi'] == '3.1.0'
    assert spec['paths']['/foo']['get']['parameters'][0]['schema'] == {'type': ['string', 'null']}

    app.config['OPENAPI_VERSION'] = '3.0.0'
    spec = app.spec
    osv.validate(spec)
    assert spec['openapi'] == '3.0.0'
    assert spec['paths']['/foo']['get']['parameters'][0]['schema'] == {
        'nullable': True,
        'type': 'string',
    }
