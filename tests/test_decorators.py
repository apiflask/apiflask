from .schemas import FooSchema
from apiflask import APIBlueprint
from apiflask import input


def test_deprecation_warning_for_standalone_decorators(recwarn, app, client):

    @app.get('/foo')
    @input(FooSchema)
    def foo():
        pass

    client.get('/foo')
    w = recwarn.pop(DeprecationWarning)
    assert 'The standalone decorators are deprecated,' in str(w)


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
