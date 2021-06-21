import os

import pytest

from apiflask import APIFlask


@pytest.fixture
def app():
    app = APIFlask(__name__)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_apps(monkeypatch):
    monkeypatch.syspath_prepend(
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_apps'))
    )
