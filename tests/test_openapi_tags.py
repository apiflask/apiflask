import pytest
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint


def test_tags(app, client):
    assert app.tags is None
    app.tags = [
        {
            'name': 'foo',
            'description': 'some description for foo',
            'externalDocs': {
                'description': 'Find more info about foo here',
                'url': 'https://docs.example.com/'
            }
        },
        {'name': 'bar', 'description': 'some description for bar'},
    ]

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags']
    assert {'name': 'bar', 'description': 'some description for bar'} in rv.json['tags']
    assert rv.json['tags'][0]['name'] == 'foo'
    assert rv.json['tags'][0]['description'] == 'some description for foo'
    assert rv.json['tags'][0]['externalDocs']['description'] == 'Find more info about foo here'
    assert rv.json['tags'][0]['externalDocs']['url'] == 'https://docs.example.com/'


def test_simple_tags(app, client):
    assert app.tags is None
    app.tags = ['foo', 'bar', 'baz']

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags']
    assert {'name': 'foo'} in rv.json['tags']
    assert {'name': 'bar'} in rv.json['tags']
    assert {'name': 'baz'} in rv.json['tags']


def test_simple_tag_from_blueprint(app, client):
    bp = APIBlueprint('test', __name__, tag='foo')
    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags']
    assert {'name': 'foo'} in rv.json['tags']


def test_tag_from_blueprint(app, client):
    tag = {
        'name': 'foo',
        'description': 'some description for foo',
        'externalDocs': {
            'description': 'Find more info about foo here',
            'url': 'https://docs.example.com/'
        }
    }
    bp = APIBlueprint('test', __name__, tag=tag)
    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags']
    assert rv.json['tags'][0]['name'] == 'foo'
    assert rv.json['tags'][0]['description'] == 'some description for foo'
    assert rv.json['tags'][0]['externalDocs']['description'] == 'Find more info about foo here'
    assert rv.json['tags'][0]['externalDocs']['url'] == 'https://docs.example.com/'


def test_auto_tag_from_blueprint(app, client):
    bp = APIBlueprint('foo', __name__)
    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags']
    assert {'name': 'Foo'} in rv.json['tags']


def test_skip_tag_from_blueprint(app, client):
    bp = APIBlueprint('foo', __name__)
    app.config['DOCS_HIDE_BLUEPRINTS'] = ['foo']
    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == []
    assert {'name': 'Foo'} not in rv.json['tags']


def test_path_tags(app, client):
    bp = APIBlueprint('foo', __name__)

    @bp.get('/')
    def foo():
        pass

    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/']['get']['tags'] == ['Foo']


@pytest.mark.parametrize('tag', ['test', {'name': 'test'}])
def test_path_tags_with_blueprint_tag(app, client, tag):
    bp = APIBlueprint('foo', __name__, tag=tag)

    @bp.get('/')
    def foo():
        pass

    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/']['get']['tags'] == ['test']


def test_tag_name_from_flask_blueprint(app, client):
    from flask import Blueprint
    bp = Blueprint('foo', __name__)

    @bp.route('/')
    def foo():
        pass

    app.register_blueprint(bp)

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == [{'name': 'Foo'}]
    assert rv.json['paths']['/']['get']['tags'] == ['Foo']
