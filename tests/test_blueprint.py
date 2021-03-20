from apiflask import Blueprint


def test_blueprint_object():
    bp = Blueprint('test', __name__)
    assert bp.name == 'test'
    assert hasattr(bp, 'tag')
    assert bp.tag is None


def test_blueprint_tag():
    bp = Blueprint('test', __name__, tag='foo')
    assert bp.name == 'test'
    assert bp.tag == 'foo'
