"""
Some description for my tag from module doc.
"""
from apiflask import APIFlask, Blueprint


app = APIFlask(__name__)
bp = Blueprint('foo', __name__)


@bp.get('/')
def hello():
    return {'message': 'Hello World!'}


app.register_blueprint(bp)
