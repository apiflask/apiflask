from apiflask import APIFlask, input
from apiflask import Schema
from apiflask.fields import Integer, String
from .schemas import PaginationSchema


def test_app_init(app):
    assert app
    assert hasattr(app, 'import_name')
    assert hasattr(app, 'title')
    assert 'TAGS' in app.config
    assert 'openapi' in app.blueprints


def test_json_errors(app, client):
    assert app.json_errors is True

    rv = client.get('/not-exist')
    assert rv.status_code == 404
    assert rv.headers['Content-Type'] == 'application/json'
    assert 'message' in rv.json
    assert 'detail' in rv.json
    assert rv.json['status_code'] == 404

    app = APIFlask(__name__, json_errors=False)
    assert app.json_errors is False
    rv = app.test_client().get('/not-exist')
    assert rv.status_code == 404
    assert rv.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'!DOCTYPE' in rv.data


def test_view_function_arguments_order(app, client):

    class QuerySchema(Schema):
        foo = String(required=True)
        bar = String(required=True)

    class PetSchema(Schema):
        name = String(required=True)
        age = Integer(default=123)

    @app.post('/pets/<int:pet_id>/toys/<int:toy_id>')
    @input(QuerySchema, 'query')
    @input(PaginationSchema, 'query')
    @input(PetSchema)
    def test_args(pet_id, toy_id, query, pagination, body):
        return {'pet_id': pet_id, 'toy_id': toy_id,
                'foo': query['foo'], 'bar': query['bar'], 'pagination': pagination, **body}

    rv = client.post('/pets/1/toys/3?foo=yes&bar=no',
                     json={'name': 'dodge', 'age': 5})
    assert rv.status_code == 200
    assert rv.json['pet_id'] == 1
    assert rv.json['toy_id'] == 3
    assert rv.json['foo'] == 'yes'
    assert rv.json['bar'] == 'no'
    assert rv.json['name'] == 'dodge'
    assert rv.json['age'] == 5
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pagination']['per_page'] == 10


def test_error_callback(app, client):
    @app.error_processor
    def custom_error_handler(status_code, message, detail, headers):
        return {'message': 'something was wrong'}, 200

    @app.get('/')
    def error():
        print(a)  # noqa: F821
        return ''

    rv = client.get('/not-exist')
    assert rv.status_code == 200
    assert 'message' in rv.json
    assert rv.json['message'] == 'something was wrong'

    rv = client.get('/')
    assert rv.status_code == 200
    assert 'message' in rv.json
    assert rv.json['message'] == 'something was wrong'
