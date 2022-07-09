import pytest

from apiflask import APIFlask


def test_openapi_blueprint(app):
    assert 'openapi' in app.blueprints
    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 4
    assert 'openapi.spec' in bp_endpoints
    assert 'openapi.docs' in bp_endpoints
    assert 'openapi.swagger_ui_oauth_redirect' in bp_endpoints
    assert 'openapi.redoc' in bp_endpoints

    app = APIFlask(__name__, spec_path=None, docs_path=None, redoc_path=None)
    assert 'openapi' not in app.blueprints


def test_spec_path(app):
    assert app.spec_path

    app = APIFlask(__name__, spec_path=None)
    assert app.spec_path is None
    assert 'openapi' in app.blueprints
    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 3
    assert 'openapi.spec' not in bp_endpoints


@pytest.mark.parametrize('spec_path', ['/spec.yaml', '/spec.yml'])
def test_yaml_spec(spec_path):
    app = APIFlask(__name__, spec_path=spec_path)
    app.config['SPEC_FORMAT'] = 'yaml'
    client = app.test_client()

    rv = client.get(spec_path)
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == 'text/vnd.yaml'
    assert b'title: APIFlask' in rv.data


def test_docs_path(app):
    assert app.docs_path

    app = APIFlask(__name__, docs_path=None)
    assert app.docs_path is None

    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 2
    assert 'openapi.docs' not in bp_endpoints
    assert 'openapi.swagger_ui_oauth_redirect' not in bp_endpoints


def test_docs_oauth2_redirect_path(client):
    rv = client.get('/docs/oauth2-redirect')
    assert rv.status_code == 200
    assert b'<title>Swagger UI: OAuth2 Redirect</title>' in rv.data
    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'oauth2RedirectUrl: "/docs/oauth2-redirect"' in rv.data

    app = APIFlask(__name__, docs_oauth2_redirect_path='/docs/oauth2/redirect')
    rv = app.test_client().get('/docs/oauth2/redirect')
    assert rv.status_code == 200
    assert b'<title>Swagger UI: OAuth2 Redirect</title>' in rv.data
    rv = app.test_client().get('/docs')
    assert rv.status_code == 200
    assert b'oauth2RedirectUrl: "/docs/oauth2/redirect"' in rv.data

    app = APIFlask(__name__, docs_oauth2_redirect_path=None)
    assert app.docs_oauth2_redirect_path is None

    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 3
    assert 'openapi.docs' in bp_endpoints
    assert 'openapi.swagger_ui_oauth_redirect' not in bp_endpoints
    rv = app.test_client().get('/docs')
    assert rv.status_code == 200
    assert b'oauth2RedirectUrl' not in rv.data


def test_redoc_path(app):
    assert app.redoc_path

    app = APIFlask(__name__, redoc_path=None)
    assert app.redoc_path is None

    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 3
    assert 'openapi.redoc' not in bp_endpoints


def test_disable_openapi_with_enable_openapi_arg(app):
    assert app.enable_openapi

    app = APIFlask(__name__, enable_openapi=False)
    assert app.enable_openapi is False

    rules = list(app.url_map.iter_rules())
    bp_endpoints = [rule.endpoint for rule in rules if rule.endpoint.startswith('openapi')]
    assert len(bp_endpoints) == 0


def test_swagger_ui(client):
    # default APIFlask(docs_ui) value is swagger-ui
    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'Swagger UI' in rv.data

    app = APIFlask(__name__, docs_ui='swagger-ui')
    rv = app.test_client().get('/docs')
    assert rv.status_code == 200
    assert b'Swagger UI' in rv.data


@pytest.mark.parametrize(
    'ui_name',
    [
        ('swagger-ui', b'Swagger UI'),
        ('redoc', b'Redoc'),
        ('elements', b'Elements'),
        ('rapidoc', b'RapiDoc'),
        ('rapipdf', b'RapiPDF'),
    ]
)
def test_other_ui(ui_name):
    app = APIFlask(__name__, docs_ui=ui_name[0])
    client = app.test_client()

    rv = client.get('/docs')
    assert rv.status_code == 200
    assert ui_name[1] in rv.data


def test_openapi_blueprint_url_prefix(app):
    assert app.openapi_blueprint_url_prefix is None

    prefix = '/api'
    app = APIFlask(__name__, openapi_blueprint_url_prefix=prefix)
    assert app.openapi_blueprint_url_prefix == prefix

    client = app.test_client()
    rv = client.get('/docs')
    assert rv.status_code == 404
    rv = client.get(f'{prefix}/docs')
    assert rv.status_code == 200
