from openapi_spec_validator import validate_spec

from apiflask import APIFlask


def test_openapi_fields(app, client):
    openapi_version = '3.0.2'
    description = 'My API'
    tags = [
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
    contact = {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    }
    license = {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
    terms_of_service = 'http://example.com/terms/'
    external_docs = {
        'description': 'Find more info here',
        'url': 'https://docs.example.com/'
    }
    servers = [
        {
            'url': 'http://localhost:5000/',
            'description': 'Development server'
        },
        {
            'url': 'https://api.example.com/',
            'description': 'Production server'
        }
    ]
    app.config['OPENAPI_VERSION'] = openapi_version
    app.config['DESCRIPTION'] = description
    app.config['TAGS'] = tags
    app.config['CONTACT'] = contact
    app.config['LICENSE'] = license
    app.config['TERMS_OF_SERVICE'] = terms_of_service
    app.config['EXTERNAL_DOCS'] = external_docs
    app.config['SERVERS'] = servers

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['openapi'] == openapi_version
    assert rv.json['tags'] == tags
    assert rv.json['servers'] == servers
    assert rv.json['externalDocs'] == external_docs
    assert rv.json['info']['description'] == description
    assert rv.json['info']['contact'] == contact
    assert rv.json['info']['license'] == license
    assert rv.json['info']['termsOfService'] == terms_of_service


def test_json_spec_mimetype(app, client):
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/json'

    app.config['JSON_SPEC_MIMETYPE'] = 'application/custom.json'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/custom.json'


def test_yaml_spec_mimetype():
    app = APIFlask(__name__, spec_path='/openapi.yaml')
    client = app.test_client()

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/vnd.yaml'

    app.config['YAML_SPEC_MIMETYPE'] = 'text/custom.yaml'

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/custom.yaml'
