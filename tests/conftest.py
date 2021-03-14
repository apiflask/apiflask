import pytest

from apiflask import APIFlask


@pytest.fixture
def app():
    app = APIFlask(__name__, title='Foo', version='1.0')
    return app


@pytest.fixture
def client(app):
    return app.test_client()
