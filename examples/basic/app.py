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

@app.route('/logs', methods=['GET'])
def getLogs():
    app.logger.info('Entering get api/logs')
    f = open('/home/achyut_p/pythonscripts/logs/gunicorn.access.log', 'r')
    for x in f:
        retrieveData = x.replace('\n', '').replace('\"\"', '')
        parseLog = retrieveData.replace('-', '').replace('\"-\"', '')
        splitSmart = shlex.split(parseLog)
        hostAddr = splitSmart[0]
        date = splitSmart[1].replace('[', '')
        req = splitSmart[3]
        returnCode = splitSmart[4]
        logItem = {
            'hostname':hostAddr,
            'date':date,
            'requestDetails':req.replace(' HTTP/1.1', ''),
            'responseCode':returnCode,
            'executionTime':0
            }
        accessLogs.append(logItem)
    f.close()

    e = open('/home/achyut_p/pythonscripts/logs/gunicorn.error.log', 'r')

    for x in e:
        errorLogs.append(x)
    e.close()

    jsonLogsStruct = {'accessLogs':accessLogs, 'errorLogs':errorLogs}
    return jsonify(jsonLogsStruct)