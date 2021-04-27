import pytest

from apiflask.utils import get_reason_phrase


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
        assert rv == 'Unknown error'
