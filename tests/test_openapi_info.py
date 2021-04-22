from openapi_spec_validator import validate_spec

from apiflask import APIFlask


def test_info_title_and_version(app):
    assert app.title == 'APIFlask'
    assert app.version == '0.1.0'

    app = APIFlask(__name__, title='Foo', version='1.0')
    assert app.spec['info']['title'] == 'Foo'
    assert app.spec['info']['version'] == '1.0'


def test_other_info_fields(app, client):
    assert app.description is None
    assert app.terms_of_service is None
    assert app.contact is None
    assert app.license is None

    app.description = 'My API'
    app.terms_of_service = 'http://example.com/terms/'
    app.contact = {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    }
    app.license = {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['info']['description'] == 'My API'
    assert rv.json['info']['termsOfService'] == 'http://example.com/terms/'
    assert rv.json['info']['contact'] == {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    }
    assert rv.json['info']['license'] == {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
