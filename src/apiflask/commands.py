import json

import click
from flask import current_app
from flask.cli import with_appcontext


@click.command('spec', short_help='Show the OpenAPI spec.')
@click.option(
    '--format',
    '-f',
    type=click.Choice(['json', 'yaml', 'yml']),
    help='The format of the spec, defaults to SPEC_FORMAT config.'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='The file path to the spec file, defauts to LOCAL_SPEC_PATH config.'
)
@click.option(
    '--indent',
    '-i',
    type=int,
    help='The indentation for JSON spec, defauts to LOCAL_SPEC_JSON_INDENT config.'
)
@with_appcontext
def spec_command(format, output, indent):
    """Output the OpenAPI spec to stdout or a file.

    Check out the docs for the detailed usage:

    https://apiflask.com/openapi/#the-flask-spec-command
    """
    spec_format = format or current_app.config['SPEC_FORMAT']
    spec = current_app._get_spec(spec_format)
    output_path = output or current_app.config['LOCAL_SPEC_PATH']
    if indent is None:
        indent = current_app.config['LOCAL_SPEC_JSON_INDENT']
    json_indent = None if indent == 0 else indent

    if spec_format == 'json':
        spec = json.dumps(spec, indent=json_indent)

    # output to stdout
    click.echo(spec)

    # output to local file
    if output_path:
        with open(output_path, 'w') as f:
            click.echo(spec, file=f)
