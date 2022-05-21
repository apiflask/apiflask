from openapi_spec_validator import validate_spec

from apiflask import APIFlask
from apiflask.security import HTTPBasicAuth
from apiflask.security import HTTPTokenAuth


def test_default_auth_error_handler(app, client):
    auth = HTTPTokenAuth()

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/foo')
    assert rv.status_code == 401
    assert rv.headers['Content-Type'] == 'application/json'
    assert 'message' in rv.json
    assert rv.json['message'] == 'Unauthorized'
    assert 'WWW-Authenticate' in rv.headers


def test_bypass_default_auth_error_handler():
    app = APIFlask(__name__, json_errors=False)
    auth = HTTPTokenAuth()

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        pass

    rv = app.test_client().get('/foo')
    assert rv.status_code == 401
    assert rv.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'Unauthorized' in rv.data
    assert 'WWW-Authenticate' in rv.headers


def test_custom_auth_error_handler(app, client):
    auth = HTTPTokenAuth()

    @auth.error_handler
    def handle_auth_error(status_code):
        return 'auth error', status_code

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/foo')
    assert rv.status_code == 401
    assert rv.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'auth error' in rv.data
    assert 'WWW-Authenticate' in rv.headers


def test_auth_error_processor(app, client):
    auth = HTTPTokenAuth()

    @auth.error_processor
    def auth_error_processor(e):
        assert e.status_code == 401
        assert e.message == 'Unauthorized'
        assert e.detail == {}
        assert e.headers == {}
        return {'message': 'custom auth error message'}, e.status_code

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        pass

    rv = client.get('/foo')
    assert rv.status_code == 401
    assert rv.headers['Content-Type'] == 'application/json'
    assert 'message' in rv.json
    assert rv.json['message'] == 'custom auth error message'
    assert 'WWW-Authenticate' in rv.headers


def test_current_user_as_property(app, client):
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        if username == 'foo' and password == 'bar':
            return {'user': 'foo'}

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        return auth.current_user

    rv = client.get('/foo', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}


def test_combine_security_schemes(app, client):
    auth = HTTPTokenAuth()

    app.config['SECURITY_SCHEMES'] = {
        'BasicAuth': {
            'type': 'http',
            'scheme': 'basic',
        },
    }

    @app.route('/')
    @app.auth_required(auth)
    def hello():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['components']['securitySchemes']['BearerAuth'] == \
        {'type': 'http', 'scheme': 'bearer'}
    assert rv.json['components']['securitySchemes']['BasicAuth'] == \
        app.config['SECURITY_SCHEMES']['BasicAuth']


def test_doc_security_overwrite(app, client):
    auth = HTTPTokenAuth()

    app.config['SECURITY_SCHEMES'] = {
        'BasicAuth': {
            'type': 'http',
            'scheme': 'basic',
        },
    }

    @app.route('/')
    @app.auth_required(auth)
    @app.doc(security='BasicAuth')
    def hello():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/']['get']['security'] == [{'BasicAuth': []}]
