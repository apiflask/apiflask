import io

from werkzeug.datastructures import FileStorage

from .schemas import FilesListSchema
from .schemas import FilesSchema


def test_file_field(app, client):
    @app.post('/')
    @app.input(FilesSchema, location='files')
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
        content_type='multipart/form-data'
    )
    assert rv.status_code == 200
    assert rv.json == {'image': True}

    rv = client.post(
        '/',
        data={
            'image': 'test',
        },
        content_type='multipart/form-data'
    )
    assert rv.status_code == 400
    assert rv.json['detail']['files']['image'] == ['Not a valid file.']


def test_multiple_file_field(app, client):
    @app.post('/')
    @app.input(FilesListSchema, location='files')
    def index(files_list_data):
        data = {'images': True}
        for f in files_list_data['images']:
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
        content_type='multipart/form-data'
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
        content_type='multipart/form-data'
    )
    assert rv.status_code == 400
    assert rv.json['detail']['files']['images']['2'] == ['Not a valid file.']
