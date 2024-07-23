import io
from importlib.metadata import version

import pytest
from packaging.version import parse
from werkzeug.datastructures import FileStorage

from .schemas import Files
from .schemas import FilesList
from apiflask import Schema
from apiflask.fields import Config


def test_file_field(app, client):
    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data):
        data = {}
        if 'image' in files_data and isinstance(files_data['image'], FileStorage):
            data['image'] = True
        return data

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    assert 'image' in rv.json['components']['schemas']['Files']['properties']
    assert rv.json['components']['schemas']['Files']['properties']['image']['type'] == 'string'
    assert rv.json['components']['schemas']['Files']['properties']['image']['format'] == 'binary'

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b'test'), 'test.jpg'),
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {'image': True}

    rv = client.post(
        '/',
        data={
            'image': 'test',
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 422
    assert rv.json['detail']['files']['image'] == ['Not a valid file.']


@pytest.mark.skipif(
    parse(version('flask-marshmallow')) < parse('1.2.1'),
    reason='Need flask_marshmallow 1.2.1 for processing empty file field',
)
def test_empty_file_field(app, client):
    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data):
        data = {}
        if 'image' in files_data and isinstance(files_data['image'], FileStorage):
            data['image'] = True
        return data

    rv = client.post(
        '/',
        data={
            'image': '',
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {}


def test_multiple_file_field(app, client):
    @app.post('/')
    @app.input(FilesList, location='files')
    def index(files_data):
        data = {'images': True}
        for f in files_data['images']:
            if not isinstance(f, FileStorage):
                data['images'] = False
        return data

    rv = client.post(
        '/',
        data={
            'images': [
                (io.BytesIO(b'test0'), 'test0.jpg'),
                (io.BytesIO(b'test1'), 'test1.jpg'),
                (io.BytesIO(b'test2'), 'test2.jpg'),
            ]
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {'images': True}

    rv = client.post(
        '/',
        data={
            'images': [
                (io.BytesIO(b'test0'), 'test0.jpg'),
                (io.BytesIO(b'test1'), 'test1.jpg'),
                'test2',
            ]
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 422
    assert rv.json['detail']['files']['images']['2'] == ['Not a valid file.']


def test_config_field(app, client):
    app.config['API_TITLE'] = 'Pet API'

    class GoodSchema(Schema):
        title = Config('API_TITLE')

    class BadSchema(Schema):
        description = Config('API_DESCRIPTION')

    @app.get('/good')
    @app.output(GoodSchema)
    def good():
        return {}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    rv = client.get('/good')
    assert rv.status_code == 200
    assert rv.json == {'title': 'Pet API'}

    with pytest.raises(ValueError, match=r'The key.*is not found in the app config.'):
        with app.app_context():
            bad = BadSchema()
            bad.dump({})
