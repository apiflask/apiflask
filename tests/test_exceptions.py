import pytest

from apiflask.exceptions import abort_json
from apiflask.exceptions import HTTPError
from apiflask.exceptions import default_error_handler
from apiflask.utils import get_reason_phrase


@pytest.mark.parametrize('kwargs', [
    {},
    {'message': 'bad'},
    {'message': 'bad', 'detail': {'location': 'json'}},
    {'message': 'bad', 'detail': {'location': 'json'}, 'headers': {'X-FOO': 'bar'}}
])
def test_httperror(app, client, kwargs):
    @app.get('/foo')
    def foo():
        raise HTTPError(400, **kwargs)

    rv = client.get('/foo')
    assert rv.status_code == 400
    if 'message' not in kwargs:
        assert rv.json['message'] == 'Bad Request'
    else:
        assert rv.json['message'] == 'bad'
    if 'detail' not in kwargs:
        assert rv.json['detail'] == {}
    else:
        assert rv.json['detail'] == {'location': 'json'}
    if 'headers' in kwargs:
        assert rv.headers['X-FOO'] == 'bar'


@pytest.mark.parametrize('kwargs', [
    {},
    {'message': 'missing'},
    {'message': 'missing', 'detail': {'location': 'query'}},
    {'message': 'missing', 'detail': {'location': 'query'}, 'headers': {'X-BAR': 'foo'}}
])
def test_abort_json(app, client, kwargs):
    @app.get('/bar')
    def bar():
        abort_json(404, **kwargs)

    rv = client.get('/bar')
    assert rv.status_code == 404
    if 'message' not in kwargs:
        assert rv.json['message'] == 'Not Found'
    else:
        assert rv.json['message'] == 'missing'
    if 'detail' not in kwargs:
        assert rv.json['detail'] == {}
    else:
        assert rv.json['detail'] == {'location': 'query'}
    if 'headers' in kwargs:
        assert rv.headers['X-BAR'] == 'foo'


@pytest.mark.parametrize('code', [400, 404, 456, 4123])
def test_get_error_message(code):
    rv = get_reason_phrase(code)
    if code == 400:
        assert rv == 'Bad Request'
    elif code == 404:
        assert rv == 'Not Found'
    else:
        assert rv == 'Unknown error'


@pytest.mark.parametrize('kwargs', [
    {},
    {'message': 'bad'},
    {'message': 'bad', 'detail': {'location': 'json'}},
    {'message': 'bad', 'detail': {'location': 'json'}, 'headers': {'X-FOO': 'bar'}}
])
def test_default_error_handler(kwargs):
    rv = default_error_handler(400, **kwargs)
    assert rv[1] == 400
    if 'message' not in kwargs:
        assert rv[0]['message'] == 'Bad Request'
    else:
        assert rv[0]['message'] == 'bad'
    if 'detail' not in kwargs:
        assert rv[0]['detail'] == {}
    else:
        assert rv[0]['detail'] == {'location': 'json'}
    if 'headers' in kwargs:
        assert rv[2]['X-FOO'] == 'bar'


def test_invalid_error_status_code():
    with pytest.raises(LookupError):
        abort_json(200)

    with pytest.raises(LookupError):
        raise HTTPError(204)
