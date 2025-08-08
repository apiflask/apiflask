from importlib import metadata

import openapi_spec_validator as osv
import pytest
from flask.views import MethodView
from packaging.version import Version

from apiflask import APIBlueprint
from apiflask.security import APIKeyCookieAuth
from apiflask.security import APIKeyHeaderAuth
from apiflask.security import APIKeyQueryAuth
from apiflask.security import HTTPBasicAuth
from apiflask.security import HTTPTokenAuth
from apiflask.security import MultiAuth


werkzeug_version = Version(metadata.version('werkzeug'))


def test_auth_required(app, client):
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        if username == 'foo' and password == 'bar':
            return {'user': 'foo'}
        elif username == 'bar' and password == 'foo':
            return {'user': 'bar'}
        elif username == 'baz' and password == 'baz':
            return {'user': 'baz'}

    @auth.get_user_roles
    def get_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @app.route('/foo')
    @app.auth_required(auth)
    def foo():
        return auth.current_user

    @app.route('/bar')
    @app.auth_required(auth, roles=['admin'])
    def bar():
        return auth.current_user

    @app.route('/baz')
    @app.auth_required(auth, roles=['admin', 'moderator'])
    def baz():
        return auth.current_user

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/foo', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.get('/bar', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/baz', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Basic YmF6OmJheg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'scheme': 'basic',
        'type': 'http',
    }

    assert 'BasicAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/bar']['get']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/baz']['get']['security'][0]


def test_auth_required_with_methodview(app, client):
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        if username == 'foo' and password == 'bar':
            return {'user': 'foo'}
        elif username == 'bar' and password == 'foo':
            return {'user': 'bar'}
        elif username == 'baz' and password == 'baz':
            return {'user': 'baz'}

    @auth.get_user_roles
    def get_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @app.route('/')
    class Foo(MethodView):
        @app.auth_required(auth)
        def get(self):
            return auth.current_user

        @app.auth_required(auth, roles=['admin'])
        def post(self):
            return auth.current_user

        @app.auth_required(auth, roles=['admin', 'moderator'])
        def delete(self):
            return auth.current_user

    rv = client.get('/')
    assert rv.status_code == 401

    rv = client.get('/', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.post('/', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.post('/', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.delete('/', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.delete('/', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.delete('/', headers={'Authorization': 'Basic YmF6OmJheg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'scheme': 'basic',
        'type': 'http',
    }

    assert 'BasicAuth' in rv.json['paths']['/']['get']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/']['post']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/']['delete']['security'][0]


def test_auth_required_at_blueprint_before_request(app, client):
    bp = APIBlueprint('auth', __name__)
    no_auth_bp = APIBlueprint('no-auth', __name__)

    auth = HTTPTokenAuth()

    @bp.before_request
    @bp.auth_required(auth)
    def before():
        pass

    @bp.get('/foo')
    def foo():
        pass

    @bp.get('/bar')
    def bar():
        pass

    @bp.route('/baz')
    class Baz(MethodView):
        def get(self):
            pass

        def post(self):
            pass

    @no_auth_bp.get('/eggs')
    def eggs():
        return 'no auth'

    app.register_blueprint(bp)
    app.register_blueprint(no_auth_bp)

    rv = client.get('/foo')
    assert rv.status_code == 401
    rv = client.get('/bar')
    assert rv.status_code == 401
    rv = client.get('/baz')
    assert rv.status_code == 401
    rv = client.get('/eggs')
    assert rv.status_code == 200

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)

    assert 'auth' in app._auth_blueprints
    assert 'no-auth' not in app._auth_blueprints

    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'scheme': 'bearer',
        'type': 'http',
    }

    assert 'BearerAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'BearerAuth' in rv.json['paths']['/bar']['get']['security'][0]
    assert 'BearerAuth' in rv.json['paths']['/baz']['get']['security'][0]
    assert 'BearerAuth' in rv.json['paths']['/baz']['post']['security'][0]
    assert 'security' not in rv.json['paths']['/eggs']['get']


def test_lowercase_token_scheme_value(app, client):
    auth = HTTPTokenAuth(scheme='bearer')

    @app.route('/')
    @app.auth_required(auth)
    def index():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)

    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert 'BearerAuth' in rv.json['paths']['/']['get']['security'][0]


def test_auth_required_with_multiauth(app, client):
    basic_auth = HTTPBasicAuth()
    token_auth = HTTPTokenAuth()
    multi_auth = MultiAuth(basic_auth, token_auth)

    @basic_auth.verify_password
    def verify_password(username, password):
        if username == 'foo' and password == 'bar':
            return {'user': 'foo'}
        elif username == 'bar' and password == 'foo':
            return {'user': 'bar'}
        elif username == 'baz' and password == 'baz':
            return {'user': 'baz'}

    @basic_auth.get_user_roles
    def get_basic_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @token_auth.verify_token
    def verify_token(token):
        if token == 'foo_token':
            return {'user': 'foo'}
        elif token == 'bar_token':
            return {'user': 'bar'}
        elif token == 'baz_token':
            return {'user': 'baz'}

    @token_auth.get_user_roles
    def get_bearer_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @app.route('/foo')
    @app.auth_required(multi_auth)
    def foo():
        return multi_auth.current_user

    @app.route('/bar')
    @app.auth_required(multi_auth, roles=['admin'])
    def bar():
        return multi_auth.current_user

    @app.route('/baz')
    @app.auth_required(multi_auth, roles=['admin', 'moderator'])
    def baz():
        return multi_auth.current_user

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/foo', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.get('/bar', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Basic Zm9vOmJhcg=='})
    assert rv.status_code == 403

    rv = client.get('/baz', headers={'Authorization': 'Basic YmFyOmZvbw=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Basic YmF6OmJheg=='})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/foo', headers={'Authorization': 'Bearer foo_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'foo'}

    rv = client.get('/bar', headers={'Authorization': 'Bearer foo_token'})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'Authorization': 'Bearer bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'Authorization': 'Bearer bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Bearer foo_token'})
    assert rv.status_code == 403

    rv = client.get('/baz', headers={'Authorization': 'Bearer bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'Authorization': 'Bearer baz_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert 'BearerAuth' in rv.json['components']['securitySchemes']

    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'scheme': 'basic',
        'type': 'http',
    }
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'scheme': 'bearer',
        'type': 'http',
    }

    assert 'BasicAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/bar']['get']['security'][0]
    assert 'BasicAuth' in rv.json['paths']['/baz']['get']['security'][0]

    assert 'BearerAuth' in rv.json['paths']['/foo']['get']['security'][1]
    assert 'BearerAuth' in rv.json['paths']['/bar']['get']['security'][1]
    assert 'BearerAuth' in rv.json['paths']['/baz']['get']['security'][1]


@pytest.mark.skipif(
    werkzeug_version < Version('2.3.0'),
    reason='The first positional server_name parameter to set_cookie and delete_cookie is deprecated. Use the domain parameter instead.',  # noqa: E501
)
def test_apikey_auth_required_with_multiauth(app, client):
    header_auth = APIKeyHeaderAuth(name='APIKeyHeaderAuth')
    cookie_auth = APIKeyCookieAuth(name='APIKeyCookieAuth')
    query_auth = APIKeyQueryAuth(name='APIKeyQueryAuth')
    multi_auth = MultiAuth(header_auth, cookie_auth, query_auth)

    @header_auth.verify_token
    @cookie_auth.verify_token
    @query_auth.verify_token
    def verify_token(token):
        if token == 'foo_token':
            return {'user': 'foo'}
        elif token == 'bar_token':
            return {'user': 'bar'}
        elif token == 'baz_token':
            return {'user': 'baz'}

    @header_auth.get_user_roles
    @cookie_auth.get_user_roles
    @query_auth.get_user_roles
    def get_bearer_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @app.route('/foo')
    @app.auth_required(multi_auth)
    def foo():
        return multi_auth.current_user

    @app.route('/bar')
    @app.auth_required(multi_auth, roles=['admin'])
    def bar():
        return multi_auth.current_user

    @app.route('/baz')
    @app.auth_required(multi_auth, roles=['admin', 'moderator'])
    def baz():
        return multi_auth.current_user

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/bar', headers={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/baz', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'X-API-Key': 'baz_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    client.set_cookie(key='X-API-Key', value='foo_token')
    rv = client.get('/bar')
    assert rv.status_code == 403
    client.delete_cookie('X-API-Key')

    client.set_cookie(key='X-API-Key', value='bar_token')
    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie('X-API-Key')

    client.set_cookie(key='X-API-Key', value='bar_token')
    rv = client.get('/bar')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie('X-API-Key')

    client.set_cookie(key='X-API-Key', value='foo_token')
    rv = client.get('/baz')
    assert rv.status_code == 403
    client.delete_cookie('X-API-Key')

    client.set_cookie(key='X-API-Key', value='bar_token')
    rv = client.get('/baz')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie('X-API-Key')

    client.set_cookie(key='X-API-Key', value='baz_token')
    rv = client.get('/baz')
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}
    client.delete_cookie('X-API-Key')

    rv = client.get('/bar', query_string={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/foo', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', query_string={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/baz', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', query_string={'X-API-Key': 'baz_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'APIKeyHeaderAuth' in rv.json['components']['securitySchemes']
    assert 'APIKeyCookieAuth' in rv.json['components']['securitySchemes']
    assert 'APIKeyQueryAuth' in rv.json['components']['securitySchemes']

    assert rv.json['components']['securitySchemes']['APIKeyHeaderAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
    }
    assert rv.json['components']['securitySchemes']['APIKeyCookieAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'cookie',
    }
    assert rv.json['components']['securitySchemes']['APIKeyQueryAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'query',
    }

    assert 'APIKeyHeaderAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'APIKeyHeaderAuth' in rv.json['paths']['/bar']['get']['security'][0]
    assert 'APIKeyHeaderAuth' in rv.json['paths']['/baz']['get']['security'][0]

    assert 'APIKeyCookieAuth' in rv.json['paths']['/foo']['get']['security'][1]
    assert 'APIKeyCookieAuth' in rv.json['paths']['/bar']['get']['security'][1]
    assert 'APIKeyCookieAuth' in rv.json['paths']['/baz']['get']['security'][1]

    assert 'APIKeyQueryAuth' in rv.json['paths']['/foo']['get']['security'][2]
    assert 'APIKeyQueryAuth' in rv.json['paths']['/bar']['get']['security'][2]
    assert 'APIKeyQueryAuth' in rv.json['paths']['/baz']['get']['security'][2]


@pytest.mark.skipif(
    werkzeug_version >= Version('2.3.0'), reason='Old usage of set_cookie and delete_cookie.'
)
def test_apikey_auth_required_with_multiauth_with_old_version_werkzeug(app, client):
    header_auth = APIKeyHeaderAuth(name='APIKeyHeaderAuth')
    cookie_auth = APIKeyCookieAuth(name='APIKeyCookieAuth')
    query_auth = APIKeyQueryAuth(name='APIKeyQueryAuth')
    multi_auth = MultiAuth(header_auth, cookie_auth, query_auth)

    @header_auth.verify_token
    @cookie_auth.verify_token
    @query_auth.verify_token
    def verify_token(token):
        if token == 'foo_token':
            return {'user': 'foo'}
        elif token == 'bar_token':
            return {'user': 'bar'}
        elif token == 'baz_token':
            return {'user': 'baz'}

    @header_auth.get_user_roles
    @cookie_auth.get_user_roles
    @query_auth.get_user_roles
    def get_bearer_roles(user):
        if user['user'] == 'bar':
            return 'admin'
        elif user['user'] == 'baz':
            return 'moderator'
        return 'normal'

    @app.route('/foo')
    @app.auth_required(multi_auth)
    def foo():
        return multi_auth.current_user

    @app.route('/bar')
    @app.auth_required(multi_auth, roles=['admin'])
    def bar():
        return multi_auth.current_user

    @app.route('/baz')
    @app.auth_required(multi_auth, roles=['admin', 'moderator'])
    def baz():
        return multi_auth.current_user

    rv = client.get('/foo')
    assert rv.status_code == 401

    rv = client.get('/bar', headers={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/foo', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/baz', headers={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', headers={'X-API-Key': 'baz_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    client.set_cookie(key='X-API-Key', value='foo_token', server_name='localhost')
    rv = client.get('/bar')
    assert rv.status_code == 403
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    client.set_cookie(key='X-API-Key', value='bar_token', server_name='localhost')
    rv = client.get('/foo')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    client.set_cookie(key='X-API-Key', value='bar_token', server_name='localhost')
    rv = client.get('/bar')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    client.set_cookie(key='X-API-Key', value='foo_token', server_name='localhost')
    rv = client.get('/baz')
    assert rv.status_code == 403
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    client.set_cookie(key='X-API-Key', value='bar_token', server_name='localhost')
    rv = client.get('/baz')
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    client.set_cookie(key='X-API-Key', value='baz_token', server_name='localhost')
    rv = client.get('/baz')
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}
    client.delete_cookie(key='X-API-Key', server_name='localhost')

    rv = client.get('/bar', query_string={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/foo', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/bar', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', query_string={'X-API-Key': 'foo_token'})
    assert rv.status_code == 403

    rv = client.get('/baz', query_string={'X-API-Key': 'bar_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'bar'}

    rv = client.get('/baz', query_string={'X-API-Key': 'baz_token'})
    assert rv.status_code == 200
    assert rv.json == {'user': 'baz'}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'APIKeyHeaderAuth' in rv.json['components']['securitySchemes']
    assert 'APIKeyCookieAuth' in rv.json['components']['securitySchemes']
    assert 'APIKeyQueryAuth' in rv.json['components']['securitySchemes']

    assert rv.json['components']['securitySchemes']['APIKeyHeaderAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
    }
    assert rv.json['components']['securitySchemes']['APIKeyCookieAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'cookie',
    }
    assert rv.json['components']['securitySchemes']['APIKeyQueryAuth'] == {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'query',
    }

    assert 'APIKeyHeaderAuth' in rv.json['paths']['/foo']['get']['security'][0]
    assert 'APIKeyHeaderAuth' in rv.json['paths']['/bar']['get']['security'][0]
    assert 'APIKeyHeaderAuth' in rv.json['paths']['/baz']['get']['security'][0]

    assert 'APIKeyCookieAuth' in rv.json['paths']['/foo']['get']['security'][1]
    assert 'APIKeyCookieAuth' in rv.json['paths']['/bar']['get']['security'][1]
    assert 'APIKeyCookieAuth' in rv.json['paths']['/baz']['get']['security'][1]

    assert 'APIKeyQueryAuth' in rv.json['paths']['/foo']['get']['security'][2]
    assert 'APIKeyQueryAuth' in rv.json['paths']['/bar']['get']['security'][2]
    assert 'APIKeyQueryAuth' in rv.json['paths']['/baz']['get']['security'][2]
