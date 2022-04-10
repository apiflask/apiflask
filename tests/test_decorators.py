from apiflask import APIBlueprint
from apiflask import HTTPBasicAuth


def test_deprecation_warning_for_role(recwarn, app, client):
    auth = HTTPBasicAuth()

    @app.get('/foo')
    @app.auth_required(auth, role='admin')
    def foo():
        pass

    client.get('/foo')
    w = recwarn.pop(DeprecationWarning)
    assert 'The `role` parameter is deprecated and will be removed in 1.1,' in str(w)


def test_deprecation_warning_for_tag(recwarn, app, client):

    @app.get('/foo')
    @app.doc(tag='foo')
    def foo():
        pass

    client.get('/foo')
    w = recwarn.pop(DeprecationWarning)
    assert 'The `tag` parameter is deprecated and will be removed in 1.1,' in str(w)


def test_app_decorators(app):
    assert hasattr(app, 'auth_required')
    assert hasattr(app, 'input')
    assert hasattr(app, 'output')
    assert hasattr(app, 'doc')


def test_bp_decorators(app):
    bp = APIBlueprint('test', __name__)
    assert hasattr(bp, 'auth_required')
    assert hasattr(bp, 'input')
    assert hasattr(bp, 'output')
    assert hasattr(bp, 'doc')
