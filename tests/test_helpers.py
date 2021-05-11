import pytest

from apiflask import get_reason_phrase
from apiflask import output
from apiflask import pagination_builder
from apiflask import PaginationSchema


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
    @output(PaginationSchema)
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
