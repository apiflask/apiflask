import io
import typing as t

import pytest
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage

from apiflask import get_reason_phrase
from apiflask import pagination_builder
from apiflask import PaginationModel
from apiflask import PaginationSchema
from apiflask.fields import UploadFile
from apiflask.helpers import _get_fields_by_type


@pytest.mark.parametrize('code', [204, 400, 404, 456, 4123])
def test_get_reason_phrase(code):
    rv = get_reason_phrase(code)
    if code == 204:
        assert rv == 'No Content'
    elif code == 400:
        assert rv == 'Bad Request'
    elif code == 404:
        assert rv == 'Not Found'
    else:
        assert rv == 'Unknown'


def test_get_reason_phrase_default():
    rv = get_reason_phrase(1234)
    assert rv == 'Unknown'

    rv = get_reason_phrase(1234, 'Unknown error')
    assert rv == 'Unknown error'


def test_pagination_builder(app, client):
    class Pagination:
        page = 1
        per_page = 20
        pages = 100
        total = 2000
        next_num = 2
        has_next = True
        prev_num = 0
        has_prev = False

    @app.get('/pets')
    @app.output(PaginationSchema)
    def get_pets():
        pagination = Pagination()
        return pagination_builder(pagination)

    rv = client.get('/pets')
    assert rv.status_code == 200
    assert rv.json['page'] == 1
    assert rv.json['first'].endswith('/pets?page=1&per_page=20')
    assert rv.json['last'].endswith('/pets?page=100&per_page=20')
    assert rv.json['next'].endswith('/pets?page=2&per_page=20')
    assert rv.json['prev'].endswith('')
    assert rv.json['current'].endswith('/pets?page=1&per_page=20')
    assert rv.json['per_page'] == 20
    assert rv.json['pages'] == 100
    assert 'has_next' not in rv.json
    assert 'next_num' not in rv.json
    assert 'has_prev' not in rv.json
    assert 'prev_num' not in rv.json


def test_pagination_builder_with_pydantic(app, client):
    class Pagination:
        page = 1
        per_page = 20
        pages = 100
        total = 2000
        next_num = 2
        has_next = True
        prev_num = 0
        has_prev = False

    @app.get('/pets')
    @app.output(PaginationModel)
    def get_pets():
        pagination = Pagination()
        return pagination_builder(pagination, schema_type='pydantic')

    rv = client.get('/pets')
    assert rv.status_code == 200
    assert rv.json['page'] == 1
    assert rv.json['first'].endswith('/pets?page=1&per_page=20')
    assert rv.json['last'].endswith('/pets?page=100&per_page=20')
    assert rv.json['next'].endswith('/pets?page=2&per_page=20')
    assert rv.json['prev'].endswith('')
    assert rv.json['current'].endswith('/pets?page=1&per_page=20')
    assert rv.json['per_page'] == 20
    assert rv.json['pages'] == 100
    assert 'has_next' not in rv.json
    assert 'next_num' not in rv.json
    assert 'has_prev' not in rv.json
    assert 'prev_num' not in rv.json


def test_pagination_builder_exception_case(app, client):
    class Pagination:
        page = 1
        per_page = 20
        pages = 100
        total = 2000
        next_num = 2
        has_next = True
        prev_num = 0
        has_prev = False

    @app.get('/pets')
    @app.output(PaginationModel)
    def get_pets():
        pagination = Pagination()
        with pytest.raises(
            ValueError, match='Invalid schema_type parameter, should be "marshmallow" or "pydantic"'
        ):
            pagination_model = pagination_builder(pagination, schema_type='unknown')
        return pagination_model

    rv = client.get('/pets')
    assert rv.status_code == 500


def test_get_fields_by_type():
    class Files(BaseModel):
        single_file: UploadFile
        file_list: t.List[UploadFile]

    class OptionalFiles(BaseModel):
        single_file: t.Optional[UploadFile] = None
        file_list: t.Optional[t.List[UploadFile]] = None

    fs = FileStorage(io.BytesIO(b'test'), 'test.jpg')
    fs_list = [
        FileStorage(io.BytesIO(b'test'), 'test1.jpg'),
        FileStorage(io.BytesIO(b'test'), 'test2.jpg'),
        FileStorage(io.BytesIO(b'test'), 'test3.jpg'),
    ]
    files = Files(single_file=fs, file_list=fs_list)
    assert _get_fields_by_type(files, FileStorage) == ['single_file']
    assert _get_fields_by_type(files, t.List[UploadFile]) == ['file_list']

    optional_files = OptionalFiles()
    assert _get_fields_by_type(optional_files, UploadFile) == ['single_file']
    assert _get_fields_by_type(optional_files, t.List[UploadFile]) == ['file_list']
