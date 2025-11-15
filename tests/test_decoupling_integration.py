import openapi_spec_validator as osv

from apiflask import Schema
from apiflask.fields import Field
from apiflask.fields import Integer
from apiflask.fields import String


class PetIn(Schema):
    """Input schema for pet."""

    name = String(required=True)
    age = Integer()


class PetOut(Schema):
    """Output schema for pet."""

    id = Integer()
    name = String()
    age = Integer()


class BaseResponseSchema(Schema):
    """Base response wrapper schema."""

    message = String()
    status = Integer()
    data = Field()


def test_schema_name_resolver_with_adapter(app, client):
    """Test that schema name resolver uses adapter."""

    @app.post('/pets')
    @app.input(PetIn)
    @app.output(PetOut, status_code=201)
    def create_pet(json_data):
        return {'id': 1, 'name': json_data['name'], 'age': json_data.get('age', 0)}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)

    # Check that schema names are resolved correctly
    assert 'PetIn' in rv.json['components']['schemas']
    assert 'PetOut' in rv.json['components']['schemas']


def test_body_schema_registration_with_reference(app, client):
    """Test that body schemas are registered and referenced correctly."""

    @app.post('/items')
    @app.input(PetIn)
    def create_item(json_data):
        return {'success': True}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check that schema is registered in components
    assert 'PetIn' in rv.json['components']['schemas']

    # Check that request body uses $ref
    request_body = rv.json['paths']['/items']['post']['requestBody']
    schema = request_body['content']['application/json']['schema']
    assert '$ref' in schema
    assert schema['$ref'] == '#/components/schemas/PetIn'


def test_body_schema_registration_duplicate_handling(app, client):
    """Test that duplicate schemas are handled correctly."""

    @app.post('/pets')
    @app.input(PetIn)
    def create_pet(json_data):
        return {'id': 1}

    @app.put('/pets/<int:pet_id>')
    @app.input(PetIn)
    def update_pet(pet_id, json_data):
        return {'id': pet_id}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Both endpoints should reference the same schema
    post_schema = rv.json['paths']['/pets']['post']['requestBody']['content']['application/json'][
        'schema'
    ]
    put_schema = rv.json['paths']['/pets/{pet_id}']['put']['requestBody']['content'][
        'application/json'
    ]['schema']

    assert post_schema == put_schema
    assert post_schema['$ref'] == '#/components/schemas/PetIn'

    # Schema should only be registered once
    assert 'PetIn' in rv.json['components']['schemas']
    assert 'PetIn1' not in rv.json['components']['schemas']


def test_body_schema_registration_with_dict(app, client):
    """Test that dict schemas are handled correctly."""
    dict_schema = {'name': String(required=True), 'value': Integer()}

    @app.post('/data')
    @app.input(dict_schema, schema_name='DataInput')
    def create_data(json_data):
        return {'success': True}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check that schema is registered
    assert 'DataInput' in rv.json['components']['schemas']

    # Check reference
    request_body = rv.json['paths']['/data']['post']['requestBody']
    schema = request_body['content']['application/json']['schema']
    assert schema['$ref'] == '#/components/schemas/DataInput'


def test_body_schema_registration_generated_schemas(app, client):
    """Test that generated schemas get unique names."""
    dict_schema1 = {'field1': String()}
    dict_schema2 = {'field2': Integer()}

    @app.post('/endpoint1')
    @app.input(dict_schema1)
    def endpoint1(json_data):
        return {}

    @app.post('/endpoint2')
    @app.input(dict_schema2)
    def endpoint2(json_data):
        return {}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Generated schemas should have unique names
    schemas = rv.json['components']['schemas']
    generated_schemas = [name for name in schemas if name.startswith('Generated')]

    assert len(generated_schemas) == 2
    assert 'GeneratedSchema' in generated_schemas
    assert 'GeneratedSchema1' in generated_schemas


def test_parameters_use_openapi_helper(app, client):
    """Test that query parameters use openapi_helper."""

    class QuerySchema(Schema):
        search = String()
        limit = Integer()

    @app.get('/search')
    @app.input(QuerySchema, location='query')
    def search(query_data):
        return {'results': []}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check that parameters are extracted correctly
    params = rv.json['paths']['/search']['get']['parameters']
    assert len(params) == 2

    param_names = [p['name'] for p in params]
    assert 'search' in param_names
    assert 'limit' in param_names

    # All should be query parameters
    assert all(p['in'] == 'query' for p in params)


def test_headers_schema_uses_openapi_helper(app, client):
    """Test that response headers use openapi_helper."""

    class HeaderSchema(Schema):
        x_rate_limit = Integer(data_key='X-RateLimit-Limit')
        x_rate_remaining = Integer(data_key='X-RateLimit-Remaining')

    @app.get('/status')
    @app.output(PetOut, headers=HeaderSchema)
    def get_status():
        return {'id': 1, 'name': 'Test', 'age': 5}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check response headers
    response = rv.json['paths']['/status']['get']['responses']['200']
    assert 'headers' in response

    headers = response['headers']
    assert 'X-RateLimit-Limit' in headers
    assert 'X-RateLimit-Remaining' in headers

    # Headers should have schema definitions
    assert 'schema' in headers['X-RateLimit-Limit']
    assert headers['X-RateLimit-Limit']['schema']['type'] == 'integer'


def test_base_response_schema_uses_openapi_helper(app, client):
    """Test that base response schema uses openapi_helper."""
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
    app.config['BASE_RESPONSE_DATA_KEY'] = 'data'

    @app.get('/items')
    @app.output(PetOut)
    def get_items():
        return {'message': 'Success', 'status': 200, 'data': {'id': 1, 'name': 'Test', 'age': 5}}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check that response schema includes base response structure
    response = rv.json['paths']['/items']['get']['responses']['200']
    schema = response['content']['application/json']['schema']

    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'message' in schema['properties']
    assert 'status' in schema['properties']
    assert 'data' in schema['properties']


def test_base_response_schema_with_dict(app, client):
    """Test base response schema with dict configuration."""
    app.config['BASE_RESPONSE_SCHEMA'] = {
        'properties': {
            'success': {'type': 'boolean'},
            'data': {'type': 'object'},
        },
        'type': 'object',
    }
    app.config['BASE_RESPONSE_DATA_KEY'] = 'data'

    @app.get('/test')
    @app.output(PetOut)
    def test_endpoint():
        return {'success': True, 'data': {'id': 1, 'name': 'Test', 'age': 5}}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    response = rv.json['paths']['/test']['get']['responses']['200']
    schema = response['content']['application/json']['schema']

    assert 'properties' in schema
    assert 'success' in schema['properties']
    assert 'data' in schema['properties']


def test_path_parameters_use_openapi_helper(app, client):
    """Test that path parameters are processed correctly."""

    class PathSchema(Schema):
        pet_id = Integer(required=True)

    @app.get('/pets/<int:pet_id>')
    @app.input(PathSchema, location='path')
    def get_pet(pet_id, path_data):
        return {'id': pet_id, 'name': 'Test', 'age': 5}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Check path parameters
    params = rv.json['paths']['/pets/{pet_id}']['get']['parameters']
    path_params = [p for p in params if p['in'] == 'path']

    assert len(path_params) >= 1
    param_names = [p['name'] for p in path_params]
    assert 'pet_id' in param_names


def test_multiple_content_types_body_schema(app, client):
    """Test body schema registration with multiple content types."""

    @app.post('/data')
    @app.input(PetIn, location='json_or_form')
    def create_data(data):
        return {'success': True}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    request_body = rv.json['paths']['/data']['post']['requestBody']

    # Should have both content types
    assert 'application/json' in request_body['content']
    assert 'application/x-www-form-urlencoded' in request_body['content']

    # Both should reference the same schema
    json_schema = request_body['content']['application/json']['schema']
    form_schema = request_body['content']['application/x-www-form-urlencoded']['schema']

    assert json_schema == form_schema
    assert '$ref' in json_schema


def test_unique_schema_names_for_different_schemas(app, client):
    """Test that different schemas with same name get unique references."""

    class ItemSchema(Schema):
        name = String()

    # Create two different schemas with potential name collision
    @app.post('/items1')
    @app.input(ItemSchema)
    def create_item1(json_data):
        return {}

    @app.post('/items2')
    @app.input(ItemSchema)
    def create_item2(json_data):
        return {}

    rv = client.get('/openapi.json')
    assert rv.status_code == 200

    # Validate OpenAPI spec
    osv.validate(rv.json)

    # Same schema class should be registered once and reused
    assert 'ItemSchema' in rv.json['components']['schemas']

    post1_schema = rv.json['paths']['/items1']['post']['requestBody']['content'][
        'application/json'
    ]['schema']
    post2_schema = rv.json['paths']['/items2']['post']['requestBody']['content'][
        'application/json'
    ]['schema']

    # Should reference the same schema
    assert post1_schema == post2_schema
