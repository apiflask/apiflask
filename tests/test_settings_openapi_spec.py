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
    client = app.test_client()

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/vnd.yaml'

    app.config['YAML_SPEC_MIMETYPE'] = 'text/custom.yaml'

    rv = client.get('/openapi.yaml')
    assert rv.status_code == 200
    assert rv.mimetype == 'text/custom.yaml'


def test_spec_format(app, cli_runner):
    app.config['SPEC_FORMAT'] = 'yaml'

    result = cli_runner.invoke(spec_command)
    assert 'title: APIFlask' in result.output


def test_local_spec_path(app, cli_runner, tmp_path):
    local_spec_path = tmp_path / 'api.json'
    app.config['LOCAL_SPEC_PATH'] = local_spec_path

    result = cli_runner.invoke(spec_command)
    assert 'openapi' in result.output
    with open(local_spec_path) as f:
        assert json.loads(f.read()) == app._spec


@pytest.mark.parametrize('indent', [0, 2, 4])
def test_local_spec_json_indent(app, cli_runner, indent):
    app.config['LOCAL_SPEC_JSON_INDENT'] = indent

    result = cli_runner.invoke(spec_command)
    if indent == 0:
        assert '{"info": {' in result.output
    else:
        assert f'{{\n{" " * indent}"info": {{' in result.output
