from apiflask import APIBlueprint


def test_blueprint_object():
    bp = APIBlueprint('test', __name__)
    assert bp.name == 'test'
    assert hasattr(bp, 'tag')
    assert bp.tag is None


def test_blueprint_tag():
    bp = APIBlueprint('test', __name__, tag='foo')
    assert bp.name == 'test'
    assert bp.tag == 'foo'
