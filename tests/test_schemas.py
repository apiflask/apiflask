import openapi_spec_validator as osv
import pytest

from apiflask.schemas import EmptySchema
from apiflask.schemas import FileSchema


def test_file_schema(app, client):
    @app.get('/image')
    @app.output(
        FileSchema(type='string', format='binary'),
        content_type='image/png',
        description='An image file',
    )
    def get_image():
        return 'file'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    content = rv.json['paths']['/image']['get']['responses']['200']['content']
    assert 'image/png' in content
    assert content['image/png']['schema'] == {'type': 'string', 'format': 'binary'}
    rv = client.get('/image')
    assert rv.status_code == 200


def test_file_schema_repr():
    f = FileSchema(type='string', format='binary')
    assert repr(f) == f'schema: \n  type: {f.type}\n  format: {f.format}'


@pytest.mark.parametrize('schema', [{}, EmptySchema])
def test_empty_schema(app, client, schema):
    @app.route('/foo')
    @app.output(schema, status_code=204)
    def empty_reposonse():
        return ''

    @app.route('/bar')
    @app.output(schema, content_type='image/png')
    def empty_schema():
        return ''

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert 'content' not in rv.json['paths']['/foo']['get']['responses']['204']

    assert 'content' in rv.json['paths']['/bar']['get']['responses']['200']
    assert (
        rv.json['paths']['/bar']['get']['responses']['200']['content']['image/png']['schema'] == {}
    )
