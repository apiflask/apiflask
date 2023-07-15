from flask.views import MethodView
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint
from apiflask.security import HTTPBasicAuth
from apiflask.security import HTTPTokenAuth


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
    validate_spec(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'scheme': 'basic',
        'type': 'http'
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
    validate_spec(rv.json)
    assert 'BasicAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BasicAuth'] == {
        'scheme': 'basic',
        'type': 'http'
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
    validate_spec(rv.json)

    assert 'auth' in app._auth_blueprints
    assert 'no-auth' not in app._auth_blueprints

    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert rv.json['components']['securitySchemes']['BearerAuth'] == {
        'scheme': 'bearer',
        'type': 'http'
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
    validate_spec(rv.json)

    assert 'BearerAuth' in rv.json['components']['securitySchemes']
    assert 'BearerAuth' in rv.json['paths']['/']['get']['security'][0]
