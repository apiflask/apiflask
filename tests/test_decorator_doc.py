import pytest
from flask.views import MethodView
from openapi_spec_validator import validate_spec

from .schemas import Foo


def test_doc_summary_and_description(app, client):
    @app.route('/foo')
    @app.doc(summary='summary from doc decorator')
    def foo():
        pass

    @app.route('/bar')
    @app.doc(summary='summary for bar', description='some description for bar')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['summary'] == 'summary from doc decorator'
    assert 'description' not in rv.json['paths']['/foo']['get']
    assert rv.json['paths']['/bar']['get']['summary'] == 'summary for bar'
    assert rv.json['paths']['/bar']['get']['description'] == 'some description for bar'


def test_doc_summary_and_description_with_methodview(app, client):
    @app.route('/baz')
    class Baz(MethodView):
        @app.doc(summary='summary from doc decorator')
        def get(self):
            pass

        @app.doc(summary='summary for baz', description='some description for baz')
        def post(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/baz']['get']['summary'] == 'summary from doc decorator'
    assert 'description' not in rv.json['paths']['/baz']['get']
    assert rv.json['paths']['/baz']['post']['summary'] == 'summary for baz'
    assert rv.json['paths']['/baz']['post']['description'] == 'some description for baz'


def test_doc_tags(app, client):
    app.tags = ['foo', 'bar']

    @app.route('/foo')
    @app.doc(tags=['foo'])
    def foo():
        pass

    @app.route('/bar')
    @app.doc(tags=['foo', 'bar'])
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['tags'] == ['foo']
    assert rv.json['paths']['/bar']['get']['tags'] == ['foo', 'bar']


def test_doc_tags_with_methodview(app, client):
    @app.route('/baz')
    class Baz(MethodView):
        @app.doc(tags=['foo'])
        def get(self):
            pass

        @app.doc(tags=['foo', 'bar'])
        def post(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/baz']['get']['tags'] == ['foo']
    assert rv.json['paths']['/baz']['post']['tags'] == ['foo', 'bar']


def test_doc_hide(app, client):
    @app.route('/foo')
    @app.doc(hide=True)
    def foo():
        pass

    @app.get('/baz')
    def get_baz():
        pass

    @app.post('/baz')
    @app.doc(hide=True)
    def post_baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/foo' not in rv.json['paths']
    assert '/baz' in rv.json['paths']
    assert 'get' in rv.json['paths']['/baz']
    assert 'post' not in rv.json['paths']['/baz']


def test_doc_hide_with_methodview(app, client):
    @app.route('/bar')
    class Bar(MethodView):
        def get(self):
            pass

        @app.doc(hide=True)
        def post(self):
            pass

    @app.route('/secret')
    class Secret(MethodView):
        @app.doc(hide=True)
        def get(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '/bar' in rv.json['paths']
    assert 'get' in rv.json['paths']['/bar']
    assert 'post' not in rv.json['paths']['/bar']
    assert '/secret' in rv.json['paths']


def test_doc_deprecated(app, client):
    @app.route('/foo')
    @app.doc(deprecated=True)
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['deprecated']


def test_doc_deprecated_with_methodview(app, client):
    @app.route('/foo')
    class FooAPI(MethodView):
        @app.doc(deprecated=True)
        def get(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['deprecated']


def test_doc_responses(app, client):
    @app.route('/foo')
    @app.input(Foo)
    @app.output(Foo)
    @app.doc(responses={200: 'success', 400: 'bad', 404: 'not found', 500: 'server error'})
    def foo():
        pass

    @app.route('/bar')
    @app.input(Foo)
    @app.output(Foo)
    @app.doc(responses=[200, 400, 404, 500])
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '200' in rv.json['paths']['/foo']['get']['responses']
    assert '400' in rv.json['paths']['/foo']['get']['responses']
    # overwrite existing error descriptions
    assert rv.json['paths']['/foo']['get']['responses'][
        '200']['description'] == 'success'
    assert rv.json['paths']['/foo']['get']['responses'][
        '400']['description'] == 'bad'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '404']['description'] == 'not found'
    assert '500' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '500']['description'] == 'server error'

    assert '200' in rv.json['paths']['/bar']['get']['responses']
    assert '400' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '200']['description'] == 'Successful response'
    assert rv.json['paths']['/bar']['get']['responses'][
        '400']['description'] == 'Bad Request'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '404']['description'] == 'Not Found'
    assert '500' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '500']['description'] == 'Internal Server Error'


def test_doc_responses_with_methodview(app, client):
    @app.route('/foo')
    class FooAPI(MethodView):
        @app.input(Foo)
        @app.output(Foo)
        @app.doc(responses={200: 'success', 400: 'bad', 404: 'not found', 500: 'server error'})
        def get(self):
            pass

    @app.route('/bar')
    class BarAPI(MethodView):
        @app.input(Foo)
        @app.output(Foo)
        @app.doc(responses=[200, 400, 404, 500])
        def get(self):
            pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert '200' in rv.json['paths']['/foo']['get']['responses']
    assert '400' in rv.json['paths']['/foo']['get']['responses']
    # don't overwrite exist error description
    assert rv.json['paths']['/foo']['get']['responses'][
        '200']['description'] == 'success'
    assert rv.json['paths']['/foo']['get']['responses'][
        '400']['description'] == 'bad'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '404']['description'] == 'not found'
    assert '500' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/foo']['get']['responses'][
        '500']['description'] == 'server error'

    assert '200' in rv.json['paths']['/bar']['get']['responses']
    assert '400' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '200']['description'] == 'Successful response'
    assert rv.json['paths']['/bar']['get']['responses'][
        '400']['description'] == 'Bad Request'
    assert '404' in rv.json['paths']['/foo']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '404']['description'] == 'Not Found'
    assert '500' in rv.json['paths']['/bar']['get']['responses']
    assert rv.json['paths']['/bar']['get']['responses'][
        '500']['description'] == 'Internal Server Error'


def test_doc_operationid(app, client):
    @app.route('/foo')
    @app.doc(operation_id='getSomeFoo')
    def foo():
        pass

    @app.route('/bar')
    def bar():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['operationId'] == 'getSomeFoo'
    assert 'operationId' not in rv.json['paths']['/bar']['get']


def test_doc_security(app, client):
    @app.route('/foo')
    @app.doc(security='ApiKeyAuth')
    def foo():
        pass

    @app.route('/bar')
    @app.doc(security=['BasicAuth', 'ApiKeyAuth'])
    def bar():
        pass

    @app.route('/baz')
    @app.doc(security=[{'OAuth2': ['read', 'write']}])
    def baz():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/foo']['get']['security'] == [{'ApiKeyAuth': []}]
    assert rv.json['paths']['/bar']['get']['security'] == [
        {'BasicAuth': []}, {'ApiKeyAuth': []}
    ]
    assert rv.json['paths']['/baz']['get']['security'] == [{'OAuth2': ['read', 'write']}]


def test_doc_security_invalid_value(app):

    @app.route('/foo')
    @app.doc(security={'BasicAuth': []})
    def foo():
        pass

    with pytest.raises(ValueError):
        app.spec
