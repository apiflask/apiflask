import io
import typing as t
from importlib.metadata import version

import pytest
from packaging.version import parse
from pydantic import AfterValidator
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage

from .schemas import Files
from .schemas import FilesList
from apiflask import Schema
from apiflask.fields import Config
from apiflask.fields import UploadFile
from apiflask.validators import validate_file_size
from apiflask.validators import validate_file_type


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


def test_file_model(app, client):
    class Files(BaseModel):
        image: UploadFile

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {}
        if 'image' in files_data.model_dump() and isinstance(files_data.image, FileStorage):
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
    assert rv.json['detail']['files']['image'] == ['Value error, Not a valid file.']


def test_file_model_in_location_form_and_files(app, client):
    class Files(BaseModel):
        image: UploadFile
        description: str

    @app.post('/')
    @app.input(Files, location='form_and_files')
    def index(form_and_files_data: Files):
        data = {}
        if 'image' in form_and_files_data.model_dump() and isinstance(
            form_and_files_data.image, FileStorage
        ):
            data['image'] = True

        data['description'] = form_and_files_data.description
        return data

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b'test'), 'test.jpg'),
            'description': 'This is a image.',
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {'image': True, 'description': 'This is a image.'}


def test_multiple_file_model(app, client):
    class Files(BaseModel):
        images: t.List[UploadFile]

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {'images': True}
        for f in files_data.images:
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


def test_empty_file_model(app, client):
    class Files(BaseModel):
        image: t.Optional[UploadFile] = None

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {}
        if 'image' in files_data.model_dump() and isinstance(files_data.image, FileStorage):
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


def test_empty_multiple_file_field(app, client):
    class Files(BaseModel):
        images: t.Optional[t.List[UploadFile]] = None

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {'images': True}
        if not files_data.images:
            return {}

        for f in files_data['images']:
            if not isinstance(f, FileStorage):
                data['images'] = False
        return data

    rv = client.post(
        '/',
        data={'images': 'null'},
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {}


def test_file_model_filetype_validator(app, client):
    class Files(BaseModel):
        image: t.Annotated[UploadFile, AfterValidator(validate_file_type(['.png']))]

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {}
        if 'image' in files_data.model_dump() and isinstance(files_data.image, FileStorage):
            data['png'] = True
        return data

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b'test'), 'test.png'),
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {'png': True}

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b'test'), 'test.jpg'),
        },
        content_type='multipart/form-data',
    )

    assert rv.status_code == 422
    assert rv.json['detail']['files']['image'] == [
        'Value error, Not an allowed file type. Allowed file types: [.png]'
    ]


def test_file_model_filesize_validator(app, client):
    class Files(BaseModel):
        image: t.Annotated[UploadFile, AfterValidator(validate_file_size(min='1 KiB'))]

    @app.post('/')
    @app.input(Files, location='files')
    def index(files_data: Files):
        data = {}
        if 'image' in files_data.model_dump() and isinstance(files_data.image, FileStorage):
            data['1 KiB'] = True
        return data

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b''.ljust(1024)), 'test.jpg'),
        },
        content_type='multipart/form-data',
    )
    assert rv.status_code == 200
    assert rv.json == {'1 KiB': True}

    rv = client.post(
        '/',
        data={
            'image': (io.BytesIO(b''.ljust(1000)), 'test.jpg'),
        },
        content_type='multipart/form-data',
    )

    assert rv.status_code == 422
    assert rv.json['detail']['files']['image'] == [
        'Value error, Must be greater than or equal to 1 KiB.'
    ]
