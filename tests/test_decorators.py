from apiflask import APIBlueprint


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
