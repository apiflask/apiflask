"""Some description for my tag from module doc."""
from apiflask import APIFlask, APIBlueprint


app = APIFlask(__name__)
bp = APIBlueprint('foo', __name__)


@bp.get('/')
def hello():
    return {'message': 'Hello World!'}


app.register_blueprint(bp)
