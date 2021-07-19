import json

import pytest
from openapi_spec_validator import validate_spec

from .schemas import BarSchema
from .schemas import BazSchema
from .schemas import FooSchema
from apiflask import doc
from apiflask import input
from apiflask import output
from apiflask import Schema as BaseSchema
from apiflask.fields import Integer


def test_spec(app):
    assert app.spec
    assert 'openapi' in app.spec


def test_spec_processor(app, client):
    @app.spec_processor
    def edit_spec(spec):
        assert spec['openapi'] == '3.0.3'
        spec['openapi'] = '3.0.2'
        assert app.title == 'APIFlask'
        assert spec['info']['title'] == 'APIFlask'
        spec['info']['title'] = 'Foo'
        return spec

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['openapi'] == '3.0.2'
    assert rv.json['info']['title'] == 'Foo'


@pytest.mark.parametrize('spec_format', ['json', 'yaml', 'yml'])
def test_get_spec(app, spec_format):
    spec = app._get_spec(spec_format)

    if spec_format == 'json':
        assert isinstance(spec, dict)
    else:
        assert 'title: APIFlask' in spec


def test_get_spec_force_update(app):
    app._get_spec()

    @app.route('/foo')
    @output(FooSchema)
    def foo():
        pass

    spec = app._get_spec()
    assert '/foo' not in spec['paths']

    new_spec = app._get_spec(force_update=True)
    assert '/foo' in new_spec['paths']


def test_spec_attribute(app):
    spec = app._get_spec()

    @app.route('/foo')
    @output(FooSchema)
    def foo():
        pass

    assert '/foo' not in spec['paths']
    assert '/foo' in app.spec['paths']


def test_spec_schemas(app):
    @app.route('/foo')
    @output(FooSchema(partial=True))
    def foo():
        pass

    @app.route('/bar')
    @output(BarSchema(many=True))
    def bar():
        pass

    @app.route('/baz')
    @output(BazSchema)
    def baz():
        pass

    class Spam(BaseSchema):
        id = Integer()

    @app.route('/spam')
    @output(Spam)
    def spam():
        pass

    class Schema(BaseSchema):
        id = Integer()

    @app.route('/schema')
    @output(Schema)
    def schema():
        pass

    spec = app.spec
    assert len(spec['components']['schemas']) == 5
    assert 'FooUpdate' in spec['components']['schemas']
    assert 'Bar' in spec['components']['schemas']
    assert 'Baz' in spec['components']['schemas']
    assert 'Spam' in spec['components']['schemas']
    assert 'Schema' in spec['components']['schemas']


def test_servers_and_externaldocs(app):
    assert app.external_docs is None
    assert app.servers is None

    app.external_docs = {
        'description': 'Find more info here',
        'url': 'https://docs.example.com/'
    }
    app.servers = [
        {
            'url': 'http://localhost:5000/',
            'description': 'Development server'
        },
        {
            'url': 'https://api.example.com/',
            'description': 'Production server'
        }
    ]

    rv = app.test_client().get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['externalDocs'] == {
        'description': 'Find more info here',
        'url': 'https://docs.example.com/'
    }
    assert rv.json['servers'] == [
        {
            'url': 'http://localhost:5000/',
            'description': 'Development server'
        },
        {
            'url': 'https://api.example.com/',
            'description': 'Production server'
        }
    ]


def test_auto_200_response(app, client):
    @app.get('/foo')
    def bare():
        pass

    @app.get('/bar')
    @input(FooSchema)
    def only_input():
        pass

    @app.get('/baz')
    @doc(summary='some summary')
    def only_doc():
        pass

    @app.get('/eggs')
    @output(FooSchema, 204)
    def output_204():
        pass

    @app.get('/spam')
    @doc(responses={204: 'empty'})
    def doc_responses():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '200' in rv.json['paths']['/foo']['get']['responses']
    assert '200' in rv.json['paths']['/bar']['get']['responses']
    assert '200' in rv.json['paths']['/baz']['get']['responses']
    assert '200' not in rv.json['paths']['/eggs']['get']['responses']
    assert '200' not in rv.json['paths']['/spam']['get']['responses']
    assert rv.json['paths']['/spam']['get']['responses'][
        '204']['description'] == 'empty'


def test_sync_local_json_spec(app, client, tmp_path):
    local_spec_path = tmp_path / 'openapi.json'
    app.config['SYNC_LOCAL_SPEC'] = True
    app.config['LOCAL_SPEC_PATH'] = local_spec_path
    app.config['SPEC_FORMAT'] = 'json'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)

    with open(local_spec_path) as f:
        spec_content = f.read()
        assert json.loads(spec_content) == app.spec
        assert '{\n  "info": {' in spec_content
        assert '"title": "APIFlask",' in spec_content


def test_sync_local_yaml_spec(app, client, tmp_path):
    local_spec_path = tmp_path / 'openapi.json'
    app.config['SYNC_LOCAL_SPEC'] = True
    app.config['LOCAL_SPEC_PATH'] = local_spec_path
    app.config['SPEC_FORMAT'] = 'yaml'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    with open(local_spec_path) as f:
        spec_content = f.read()
        assert spec_content == str(app.spec)
        assert 'title: APIFlask' in spec_content


def test_sync_local_spec_no_path(app):
    app.config['SYNC_LOCAL_SPEC'] = True

    with pytest.raises(TypeError):
        app.spec
