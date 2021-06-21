import json

import pytest

from apiflask.commands import spec_command


def test_flask_spec_stdout(app, cli_runner):
    result = cli_runner.invoke(spec_command)
    assert 'openapi' in result.output
    assert json.loads(result.output) == app.spec


def test_flask_spec_output(app, cli_runner, tmp_path):
    local_spec_path = tmp_path / 'openapi.json'
    result = cli_runner.invoke(spec_command, ['--output', str(local_spec_path)])
    assert 'openapi' in result.output
    with open(local_spec_path) as f:
        assert json.loads(f.read()) == app.spec


@pytest.mark.parametrize('format', ['json', 'yaml', 'yml', 'foo'])
def test_flask_spec_format(app, cli_runner, format, tmp_path):
    local_spec_path = tmp_path / 'openapi.json'

    @app.get('/')
    def hello():
        pass

    stdout_result = cli_runner.invoke(spec_command, ['--format', format])
    file_result = cli_runner.invoke(
        spec_command, ['--format', format, '--output', str(local_spec_path)]
    )
    if format == 'json':
        assert '"title": "APIFlask",' in stdout_result.output
        assert '"title": "APIFlask",' in file_result.output
    elif format.startswith('y'):
        assert 'title: APIFlask' in stdout_result.output
        assert 'title: APIFlask' in file_result.output
    else:
        assert 'Invalid value' in stdout_result.output
        assert 'Invalid value' in file_result.output


@pytest.mark.parametrize('indent', [0, 2, 4])
def test_flask_spec_indent(cli_runner, indent, tmp_path):
    local_spec_path = tmp_path / 'openapi.json'
    stdout_result = cli_runner.invoke(spec_command, ['--indent', indent])
    file_result = cli_runner.invoke(
        spec_command, ['--indent', indent, '--output', str(local_spec_path)]
    )
    if indent == 0:
        assert '{"info": {' in stdout_result.output
        assert '{"info": {' in file_result.output
    else:
        assert f'{{\n{" " * indent}"info": {{' in stdout_result.output
        assert f'{{\n{" " * indent}"info": {{' in file_result.output
