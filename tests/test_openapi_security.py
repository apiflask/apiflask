import openapi_spec_validator as osv
import pytest

from apiflask import HTTPAPIKeyAuth
from apiflask import HTTPBasicAuth
from apiflask import HTTPTokenAuth
from apiflask.security import MultiAuth


def test_httpbasicauth_security_scheme(app, client):
    auth = HTTPBasicAuth()

    @app.get('/')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'type': 'http',
        'scheme': 'basic',
    }


def test_httptokenauth_security_scheme(app, client):
    auth = HTTPTokenAuth()

    @app.get('/')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'scheme': 'bearer',
        'type': 'http',
    }


def test_deprecated_apikey_auth_security_scheme(app, client):
    auth = HTTPTokenAuth('apiKey', header='X-API-Key')

    @app.get('/')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'ApiKeyAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['ApiKeyAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
    }


def test_apikey_auth_security_scheme(app, client):
    auth = HTTPAPIKeyAuth()

    @app.get('/')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'ApiKeyAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['ApiKeyAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
    }


def test_custom_security_scheme_name(app, client):
    basic_auth = HTTPBasicAuth(security_scheme_name='basic_auth')
    apikey_auth = HTTPAPIKeyAuth(security_scheme_name='myAPIKey')

    @app.get('/foo')
    @app.auth_required(basic_auth)
    def foo():
        pass

    @app.get('/bar')
    @app.auth_required(apikey_auth)
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'basic_auth' in rv.json['components']['securitySchemes']
    assert 'myAPIKey' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['basic_auth'] == {
        'type': 'http',
        'scheme': 'basic',
    }
    assert rv.json['components']['securitySchemes']['myAPIKey'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
    }
    assert 'basic_auth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'myAPIKey' in rv.json['paths']['/bar']['get']['security'][0]


def test_unknown_auth_security_scheme(app):
    from flask_httpauth import HTTPDigestAuth

    auth = HTTPDigestAuth()

    @app.get('/')
    @app.auth_required(auth)
    def foo():
        pass

    with pytest.raises(TypeError):
        app.spec


def test_multiple_auth_names(app, client):
    auth1 = HTTPBasicAuth()
    auth2 = HTTPBasicAuth()
    auth3 = HTTPBasicAuth()

    @app.get('/foo')
    @app.auth_required(auth1)
    def foo():
        pass

    @app.get('/bar')
    @app.auth_required(auth2)
    def bar():
        pass

    @app.get('/baz')
    @app.auth_required(auth3)
    def baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert 'BasicAuth_2' in rv.json['components']['securitySchemes']
    assert 'BasicAuth_3' in rv.json['components']['securitySchemes']


def test_security_schemes_description(app, client):
    basic_auth = HTTPBasicAuth(description='some description for basic auth')
    token_auth = HTTPTokenAuth(description='some description for bearer auth')
    apikey_auth = HTTPAPIKeyAuth(description='some description for apikey auth')

    @app.get('/foo')
    @app.auth_required(basic_auth)
    def foo():
        pass

    @app.get('/bar')
    @app.auth_required(token_auth)
    def bar():
        pass

    @app.get('/baz')
    @app.auth_required(apikey_auth)
    def baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert 'ApiKeyAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'type': 'http',
        'scheme': 'basic',
        'description': 'some description for basic auth',
    }
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'type': 'http',
        'scheme': 'bearer',
        'description': 'some description for bearer auth',
    }
    assert rv.json['components']['securitySchemes']['ApiKeyAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
        'description': 'some description for apikey auth',
    }


def test_multi_auth(app, client):
    basic_auth = HTTPBasicAuth()
    token_auth = HTTPTokenAuth()
    multi_auth = MultiAuth(basic_auth, token_auth)

    @app.route('/foo')
    @app.auth_required(multi_auth)
    def foo():
        pass

    rv = client.get('/foo')
    assert rv.status_code == 401
    assert rv.headers['Content-Type'] == 'application/json'
    assert 'message' in rv.json
    assert rv.json['message'] == 'Unauthorized'
    assert 'WWW-Authenticate' in rv.headers
