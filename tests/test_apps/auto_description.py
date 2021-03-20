"""
Some description for my API.
"""
from apiflask import APIFlask


app = APIFlask(__name__)


@app.get('/')
def hello():
    return {'message': 'Hello World!'}
