from openapi_spec_validator import validate_spec

from apiflask import input, output
from apiflask import Schema
from apiflask.fields import Integer, String
from .schemas import FooSchema, PaginationSchema


def test_route_shortcuts(app, client):

    @app.get('/pet')
    @output(FooSchema)
    def test_get():
        return {'name': 'get'}

    @app.post('/pet')
    @output(FooSchema)
    def test_post():
        return {'name': 'post'}

    @app.put('/pet')
    @output(FooSchema)
    def test_put():
        return {'name': 'put'}

    @app.patch('/pet')
    @output(FooSchema)
    def test_patch():
        return {'name': 'patch'}

    @app.delete('/pet')
    @output(FooSchema)
    def test_delete():
        return {'name': 'delete'}

    rv = client.get('/pet')
    assert rv.json['name'] == 'get'

    rv = client.post('/pet')
    assert rv.json['name'] == 'post'

    rv = client.put('/pet')
    assert rv.json['name'] == 'put'

    rv = client.patch('/pet')
    assert rv.json['name'] == 'patch'

    rv = client.delete('/pet')
    assert rv.json['name'] == 'delete'

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/pet']['get']['summary'] == 'Test Get'
    assert rv.json['paths']['/pet']['post']['summary'] == 'Test Post'
    assert rv.json['paths']['/pet']['put']['summary'] == 'Test Put'
    assert rv.json['paths']['/pet']['patch']['summary'] == 'Test Patch'
    assert rv.json['paths']['/pet']['delete']['summary'] == 'Test Delete'


def test_view_function_arguments(app, client):

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
