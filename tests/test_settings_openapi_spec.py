import json

import pytest

from apiflask import APIFlask
from apiflask.commands import spec_command


def test_json_spec_mimetype(app, client):
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/json'

    app.config['JSON_SPEC_MIMETYPE'] = 'application/custom.json'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert rv.mimetype == 'application/custom.json'


def test_yaml_spec_mimetype():
    app = APIFlask(__name__, spec_path='/openapi.yaml')
    app.config['SPEC_FORMAT'] = 'yaml'
    client = app.test_client()

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/vnd.yaml'

    app.config['YAML_SPEC_MIMETYPE'] = 'text/custom.yaml'

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/custom.yaml'


@pytest.mark.parametrize('format', ['yaml', 'yml', 'json'])
def test_spec_format(app, client, cli_runner, format):
    app.config['SPEC_FORMAT'] = format

    result = cli_runner.invoke(spec_command)
    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    if format == 'json':
        assert '"title": "APIFlask",' in result.output
        assert b'"title":"APIFlask",' in rv.data
        assert rv.headers['Content-Type'] == 'application/json'
    else:
        assert 'title: APIFlask' in result.output
        assert b'title: APIFlask' in rv.data
        assert rv.headers['Content-Type'] == 'text/vnd.yaml'


def test_local_spec_path(app, cli_runner, tmp_path):
    local_spec_path = tmp_path / 'api.json'
    app.config['LOCAL_SPEC_PATH'] = local_spec_path

    result = cli_runner.invoke(spec_command)
    assert 'openapi' in result.output
    with open(local_spec_path) as f:
        assert json.loads(f.read()) == app.spec


@pytest.mark.parametrize('indent', [0, 2, 4])
def test_local_spec_json_indent(app, cli_runner, indent):
    app.config['LOCAL_SPEC_JSON_INDENT'] = indent

    result = cli_runner.invoke(spec_command)
    if indent == 0:
        assert '{"info": {' in result.output
    else:
        assert f'{{\n{" " * indent}"info": {{' in result.output
