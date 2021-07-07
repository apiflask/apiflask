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
    assert rv.json['info']['description'] == app.description
    assert rv.json['info']['termsOfService'] == app.terms_of_service
    assert rv.json['info']['contact'] == app.contact
    assert rv.json['info']['license'] == app.license


def test_info_attribute(app, client):
    assert app.info is None

    app.info = {
        'description': 'My API',
        'termsOfService': 'http://example.com',
        'contact': {
            'name': 'API Support',
            'url': 'http://www.example.com/support',
            'email': 'support@example.com'
        },
        'license': {
            'name': 'Apache 2.0',
            'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
        }
    }

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['info']['description'] == app.info['description']
    assert rv.json['info']['termsOfService'] == app.info['termsOfService']
    assert rv.json['info']['contact'] == app.info['contact']
    assert rv.json['info']['license'] == app.info['license']


def test_overwirte_info_attribute(app, client):
    assert app.info is None
    assert app.description is None
    assert app.terms_of_service is None
    assert app.contact is None
    assert app.license is None

    app.info = {
        'description': 'Not set',
        'termsOfService': 'Not set',
        'contact': {
            'name': 'Not set',
            'url': 'Not set',
            'email': 'Not set'
        },
        'license': {
            'name': 'Not set',
            'url': 'Not set'
        }
    }

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
    assert rv.json['info']['description'] == app.description
    assert rv.json['info']['termsOfService'] == app.terms_of_service
    assert rv.json['info']['contact'] == app.contact
    assert rv.json['info']['license'] == app.license
