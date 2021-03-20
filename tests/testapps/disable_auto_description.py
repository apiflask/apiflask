"""
Some description for my API.
"""
from apiflask import APIFlask


app = APIFlask(__name__)
app.config['AUTO_DESCRIPTION'] = False


@app.get('/')
def hello():
    return {'message': 'Hello World!'}
