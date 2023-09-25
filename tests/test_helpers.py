import io

import pytest
from werkzeug.datastructures import FileStorage

from apiflask import get_reason_phrase
from apiflask import pagination_builder
from apiflask import PaginationSchema
from apiflask.helpers import get_filestorage_size
from apiflask.helpers import parse_size


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


def test_get_filestorage_size():
    rv = get_filestorage_size(FileStorage(io.BytesIO(b''.ljust(1024))))
    assert rv == 1024


@pytest.mark.parametrize(
    'size',
    ['1 KB', '1 KiB', '1 MB', '1 MiB', '1 GB', '1 GiB']
)
def test_parse_size(size):
    rv = parse_size(size)
    if size == '1 KB':
        assert rv == 1000
    elif size == '1 KiB':
        assert rv == 1024
    elif size == '1 MB':
        assert rv == 1000000
    elif size == '1 MiB':
        assert rv == 1048576
    elif size == '1 GB':
        assert rv == 1000000000
    elif size == '1 GiB':
        assert rv == 1073741824


def test_parse_size_wrong_value():
    with pytest.raises(ValueError, match='Invalid size value: '):
        parse_size('wrong_format')

    with pytest.raises(ValueError, match='Invalid float value while parsing size: '):
        parse_size('1.2.3 MiB')
