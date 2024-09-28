from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


from flask import jsonify
import logging
import shlex
import json
import pytz

class LogItem:
    def __init__(self, hostname, date, requestDet, resultCode):
        self.hostname = hostname
        self.date = date
        self.requestDet = requestDet

app = APIFlask(__name__)
app.logger.setLevel(logging.ERROR)
accessLogs = []
errorLogs = []

@app.route('/hello', methods=['GET'])
def get_hello_world():
    app.logger.info('Entering get /api/hello')
    return jsonify("Hello world")