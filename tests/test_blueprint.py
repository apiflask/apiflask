from flask.views import MethodView
from openapi_spec_validator import validate_spec

from apiflask import APIBlueprint
from apiflask.security import HTTPBasicAuth
from apiflask.security import HTTPTokenAuth


def test_blueprint_object():
    bp = APIBlueprint('test', __name__)
    assert bp.name == 'test'
    assert hasattr(bp, 'tag')
    assert bp.tag is None


def test_blueprint_tag():
    bp = APIBlueprint('test', __name__, tag='foo')
    assert bp.name == 'test'
    assert bp.tag == 'foo'


def test_blueprint_enable_openapi(app, client):
    auth = HTTPBasicAuth()

    @app.get('/hello')
    @app.auth_required(auth)
    def hello():
        pass

    bp = APIBlueprint('foo', __name__, tag='test', enable_openapi=False)
    auth = HTTPTokenAuth()

    @bp.before_request
    @bp.auth_required(auth)
    def before():
        pass

    @bp.get('/foo')
    def foo():
        pass

    app.register_blueprint(bp)

    rv = client.get('/foo')
    assert rv.status_code == 401
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == []
    assert '/hello' in rv.json['paths']
    assert '/foo' not in rv.json['paths']
    assert 'BearerAuth' not in rv.json['components']['securitySchemes']


def test_blueprint_enable_openapi_with_methodview(app, client):
    auth = HTTPBasicAuth()

    @app.get('/hello')
    @app.auth_required(auth)
    def hello():
        pass

    bp = APIBlueprint('foo', __name__, tag='test', enable_openapi=False)
    auth = HTTPTokenAuth()

    @bp.before_request
    @bp.auth_required(auth)
    def before():
        pass

    @bp.route('/foo')
    class Foo(MethodView):
        def get(self):
            pass

        def post(self):
            pass

    app.register_blueprint(bp)

    rv = client.get('/foo')
    assert rv.status_code == 401
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['tags'] == []
    assert '/hello' in rv.json['paths']
    assert '/foo' not in rv.json['paths']
    assert 'BearerAuth' not in rv.json['components']['securitySchemes']
