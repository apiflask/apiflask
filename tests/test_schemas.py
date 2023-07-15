from apiflask.schemas import FileSchema


def test_file_schema(app, client):
    @app.get('/image')
    @app.output(
        FileSchema(type='string', format='binary'),
        content_type='image/png',
        description='An image file'
    )
    def get_image():
        return 'file'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    content = rv.json['paths']['/image']['get']['responses']['200']['content']
    assert 'image/png' in content
    assert content['image/png']['schema'] == {
        'type': 'string',
        'format': 'binary'
    }


def test_file_schema_repr():
    f = FileSchema(type='string', format='binary')
    assert repr(f) == f'schema: \n  type: {f.type}\n  format: {f.format}'
