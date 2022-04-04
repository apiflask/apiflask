from openapi_spec_validator import validate_spec


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


def test_info(app, client):
    app.config['INFO'] = {
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
    assert rv.json['info']['description'] == app.config['INFO']['description']
    assert rv.json['info']['termsOfService'] == app.config['INFO']['termsOfService']
    assert rv.json['info']['contact'] == app.config['INFO']['contact']
    assert rv.json['info']['license'] == app.config['INFO']['license']


def test_overwirte_info(app, client):
    app.config['INFO'] = {
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

    app.config['DESCRIPTION'] = 'My API'
    app.config['CONTACT'] = {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    }
    app.config['LICENSE'] = {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
    app.config['TERMS_OF_SERVICE'] = 'http://example.com/terms/'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['info']['description'] == app.config['DESCRIPTION']
    assert rv.json['info']['termsOfService'] == app.config['TERMS_OF_SERVICE']
    assert rv.json['info']['contact'] == app.config['CONTACT']
    assert rv.json['info']['license'] == app.config['LICENSE']


def test_security_shemes(app, client):
    app.config['SECURITY_SCHEMES'] = {
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key'
        },
        'BasicAuth': {
            'type': 'http',
            'scheme': 'basic',
        },
    }

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['components']['securitySchemes']['ApiKeyAuth'] == \
        app.config['SECURITY_SCHEMES']['ApiKeyAuth']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == \
        app.config['SECURITY_SCHEMES']['BasicAuth']
