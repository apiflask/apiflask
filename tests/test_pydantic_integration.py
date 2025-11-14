import sys

import openapi_spec_validator as osv
import pytest

from apiflask import APIFlask

# Skip all tests in this module if pydantic is not available
pydantic = pytest.importorskip('pydantic')
BaseModel = pydantic.BaseModel


class UserModel(BaseModel):
    id: int
    name: str
    email: str


class UserCreateModel(BaseModel):
    name: str
    email: str


class TestPydanticIntegration:
    """Test Pydantic model integration with APIFlask."""

    def test_input_decorator_with_pydantic_model(self):
        """Test @app.input decorator with Pydantic model."""
        app = APIFlask(__name__)

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        def create_user(json_data):
            assert isinstance(json_data, UserCreateModel)
            assert json_data.name == 'John Doe'
            assert json_data.email == 'john@example.com'
            return {'message': 'User created'}

        with app.test_client() as client:
            response = client.post('/users', json={'name': 'John Doe', 'email': 'john@example.com'})
            assert response.status_code == 200

    def test_output_decorator_with_pydantic_model(self):
        """Test @app.output decorator with Pydantic model."""
        app = APIFlask(__name__)

        @app.get('/users/<int:user_id>')
        @app.output(UserModel)
        def get_user(user_id):
            return UserModel(id=user_id, name='John Doe', email='john@example.com')

        with app.test_client() as client:
            response = client.get('/users/1')
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == 1
            assert data['name'] == 'John Doe'
            assert data['email'] == 'john@example.com'

    def test_input_validation_error(self):
        """Test validation error with Pydantic model."""
        app = APIFlask(__name__)

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        def create_user(json_data):
            return {'message': 'User created'}

        with app.test_client() as client:
            # Missing required field
            response = client.post('/users', json={'name': 'John Doe'})
            assert response.status_code == app.config['VALIDATION_ERROR_STATUS_CODE']
            data = response.get_json()
            assert 'message' in data
            assert 'detail' in data

    def test_pydantic_openapi_schema_generation(self):
        """Test OpenAPI schema generation for Pydantic models."""
        app = APIFlask(__name__)

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        @app.output(UserModel)
        def create_user(json_data):
            return UserModel(id=1, name=json_data.name, email=json_data.email)

        with app.test_client() as client:
            rv = client.get('/openapi.json')
            assert rv.status_code == 200

            # Validate OpenAPI spec
            osv.validate(rv.json)

            spec = rv.get_json()
            assert 'components' in spec or 'definitions' in spec
            # Check that the schema is generated
            assert 'paths' in spec
            assert '/users' in spec['paths']

    def test_pydantic_models_in_components_schemas(self):
        """Test that Pydantic models are correctly registered in components/schemas."""
        app = APIFlask(__name__)

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        @app.output(UserModel, status_code=201)
        def create_user(json_data):
            return UserModel(id=1, name=json_data.name, email=json_data.email)

        @app.get('/users/<int:user_id>')
        @app.output(UserModel)
        def get_user(user_id):
            return UserModel(id=user_id, name='John Doe', email='john@example.com')

        with app.test_client() as client:
            # Fetch the OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200

            # Validate OpenAPI spec
            osv.validate(rv.json)

            spec = rv.get_json()

            # Check that both Pydantic models are in components/schemas
            assert 'components' in spec
            assert 'schemas' in spec['components']
            schemas = spec['components']['schemas']

            # UserModel and UserCreateModel should be registered
            assert 'UserModel' in schemas
            assert 'UserCreateModel' in schemas

            # Check UserModel schema structure
            user_model_schema = schemas['UserModel']
            assert 'properties' in user_model_schema
            assert 'id' in user_model_schema['properties']
            assert 'name' in user_model_schema['properties']
            assert 'email' in user_model_schema['properties']
            assert user_model_schema['properties']['id']['type'] == 'integer'
            assert user_model_schema['properties']['name']['type'] == 'string'
            assert user_model_schema['properties']['email']['type'] == 'string'

            # Check UserCreateModel schema structure
            user_create_schema = schemas['UserCreateModel']
            assert 'properties' in user_create_schema
            assert 'name' in user_create_schema['properties']
            assert 'email' in user_create_schema['properties']
            assert 'id' not in user_create_schema['properties']  # Should not have id

    def test_pydantic_schema_references_in_paths(self):
        """Test that schema references in paths use correct names, not class representations."""
        app = APIFlask(__name__)

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        @app.output(UserModel, status_code=201)
        def create_user(json_data):
            return UserModel(id=1, name=json_data.name, email=json_data.email)

        @app.get('/users/<int:user_id>')
        @app.output(UserModel)
        def get_user(user_id):
            return UserModel(id=user_id, name='John Doe', email='john@example.com')

        with app.test_client() as client:
            rv = client.get('/openapi.json')
            assert rv.status_code == 200

            # Validate OpenAPI spec
            osv.validate(rv.json)

            spec = rv.get_json()

            # Check POST /users requestBody reference
            post_path = spec['paths']['/users']['post']
            assert 'requestBody' in post_path
            request_schema = post_path['requestBody']['content']['application/json']['schema']
            assert '$ref' in request_schema
            # Should be a proper reference, not a class representation
            assert request_schema['$ref'] == '#/components/schemas/UserCreateModel'
            assert '<class' not in request_schema['$ref']  # Should NOT contain <class ...>

            # Check POST /users response reference
            post_response = post_path['responses']['201']['content']['application/json']['schema']
            assert '$ref' in post_response
            assert post_response['$ref'] == '#/components/schemas/UserModel'
            assert '<class' not in post_response['$ref']

            # Check GET /users/{user_id} response reference
            get_path = spec['paths']['/users/{user_id}']['get']
            get_response = get_path['responses']['200']['content']['application/json']['schema']
            assert '$ref' in get_response
            assert get_response['$ref'] == '#/components/schemas/UserModel'
            assert '<class' not in get_response['$ref']

    def test_mixed_schemas_support(self):
        """Test that both marshmallow and Pydantic schemas can coexist."""
        from apiflask import Schema
        from apiflask.fields import String, Integer

        app = APIFlask(__name__)

        # Marshmallow schema
        class UserMarshmallowSchema(Schema):
            id = Integer()
            name = String()

        @app.get('/users/marshmallow/<int:user_id>')
        @app.output(UserMarshmallowSchema)
        def get_user_marshmallow(user_id):
            return {'id': user_id, 'name': 'John Doe'}

        @app.get('/users/pydantic/<int:user_id>')
        @app.output(UserModel)
        def get_user_pydantic(user_id):
            return UserModel(id=user_id, name='John Doe', email='john@example.com')

        with app.test_client() as client:
            # Validate OpenAPI spec with mixed schemas
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            # Test marshmallow endpoint
            response = client.get('/users/marshmallow/1')
            assert response.status_code == 200

            # Test pydantic endpoint
            response = client.get('/users/pydantic/1')
            assert response.status_code == 200

    def test_query_parameters_with_pydantic(self):
        """Test query parameter validation with Pydantic."""

        class QueryModel(BaseModel):
            page: int = 1
            per_page: int = 10
            search: str = ''

        app = APIFlask(__name__)

        @app.get('/users')
        @app.input(QueryModel, location='query')
        def list_users(query_data):
            assert isinstance(query_data, QueryModel)
            return {
                'page': query_data.page,
                'per_page': query_data.per_page,
                'search': query_data.search,
            }

        with app.test_client() as client:
            # Validate OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            response = client.get('/users?page=2&per_page=20&search=john')
            assert response.status_code == 200
            data = response.get_json()
            assert data['page'] == 2
            assert data['per_page'] == 20
            assert data['search'] == 'john'

    def test_headers_with_pydantic(self):
        """Test headers validation with Pydantic."""

        class HeaderModel(BaseModel):
            x_token: str = 'default'
            x_version: str = '1.0'

        app = APIFlask(__name__)

        @app.get('/protected')
        @app.input(HeaderModel, location='headers')
        def protected_route(headers_data):
            assert isinstance(headers_data, HeaderModel)
            return {
                'token': headers_data.x_token,
                'version': headers_data.x_version,
            }

        with app.test_client() as client:
            response = client.get(
                '/protected', headers={'X-Token': 'secret123', 'X-Version': '2.0'}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['token'] == 'secret123'
            assert data['version'] == '2.0'

            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

    def test_cookies_with_pydantic(self):
        """Test cookies validation with Pydantic."""

        class CookieModel(BaseModel):
            session_id: str = 'default'
            theme: str = 'light'

        app = APIFlask(__name__)

        @app.get('/dashboard')
        @app.input(CookieModel, location='cookies')
        def dashboard(cookies_data):
            assert isinstance(cookies_data, CookieModel)
            return {
                'session_id': cookies_data.session_id,
                'theme': cookies_data.theme,
            }

        with app.test_client() as client:
            # Flask 2.0-2.2 requires server_name as positional arg
            # Flask 2.3+ uses domain parameter instead
            import inspect

            sig = inspect.signature(client.set_cookie)
            if 'server_name' in sig.parameters and sig.parameters['server_name'].kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            ):
                # Old API (Flask 2.0-2.2)
                client.set_cookie('localhost', 'session_id', 'abc123')
                client.set_cookie('localhost', 'theme', 'dark')
            else:
                # New API (Flask 2.3+)
                client.set_cookie(key='session_id', value='abc123', domain='localhost')
                client.set_cookie(key='theme', value='dark', domain='localhost')
            response = client.get('/dashboard')
            assert response.status_code == 200
            data = response.get_json()
            assert data['session_id'] == 'abc123'
            assert data['theme'] == 'dark'

            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

    def test_path_parameters_with_pydantic(self):
        """Test path parameters validation with Pydantic."""

        class PathModel(BaseModel):
            user_id: int
            action: str

        app = APIFlask(__name__)

        @app.get('/users/<int:user_id>/<action>')
        @app.input(PathModel, location='path')
        def user_action(user_id, action, path_data):
            assert isinstance(path_data, PathModel)
            return {
                'user_id': path_data.user_id,
                'action': path_data.action,
            }

        with app.test_client() as client:
            # Validate OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            response = client.get('/users/123/delete')
            assert response.status_code == 200
            data = response.get_json()
            assert data['user_id'] == 123
            assert data['action'] == 'delete'

    def test_view_args_location_alias(self):
        """Test that 'view_args' location works as alias for 'path'."""

        class PathModel(BaseModel):
            item_id: int

        app = APIFlask(__name__)

        @app.get('/items/<int:item_id>')
        @app.input(PathModel, location='view_args')
        def get_item(item_id, view_args_data):
            assert isinstance(view_args_data, PathModel)
            return {'item_id': view_args_data.item_id}

        with app.test_client() as client:
            response = client.get('/items/456')
            assert response.status_code == 200
            data = response.get_json()
            assert data['item_id'] == 456

            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

    def test_list_type_with_typing_List(self):
        """Test list type support with typing.List[Model]."""
        from typing import List

        app = APIFlask(__name__)

        @app.get('/users')
        @app.output(List[UserModel])
        def get_users():
            return [
                UserModel(id=1, name='Alice', email='alice@example.com'),
                UserModel(id=2, name='Bob', email='bob@example.com'),
            ]

        with app.test_client() as client:
            # Test response
            response = client.get('/users')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['id'] == 1
            assert data[0]['name'] == 'Alice'
            assert data[1]['id'] == 2
            assert data[1]['name'] == 'Bob'

            # Test OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            spec = rv.get_json()
            response_schema = spec['paths']['/users']['get']['responses']['200']['content'][
                'application/json'
            ]['schema']
            # Should be array type with items referencing UserModel
            assert response_schema['type'] == 'array'
            assert 'items' in response_schema
            assert response_schema['items']['$ref'] == '#/components/schemas/UserModel'

    @pytest.mark.skipif(sys.version_info < (3, 9), reason='Native list syntax requires Python 3.9+')
    def test_list_type_with_native_list(self):
        """Test list type support with native list[Model] (Python 3.9+)."""
        app = APIFlask(__name__)

        @app.get('/users')
        @app.output(list[UserModel])
        def get_users():
            return [
                {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
                {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
            ]

        with app.test_client() as client:
            # Test response
            response = client.get('/users')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['id'] == 1
            assert data[1]['id'] == 2

            # Test OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            spec = rv.get_json()
            response_schema = spec['paths']['/users']['get']['responses']['200']['content'][
                'application/json'
            ]['schema']
            # Should be array type
            assert response_schema['type'] == 'array'
            assert 'items' in response_schema
            assert response_schema['items']['$ref'] == '#/components/schemas/UserModel'

    @pytest.mark.skipif(sys.version_info < (3, 9), reason='Native list syntax requires Python 3.9+')
    def test_list_type_with_dict_response(self):
        """Test list type with dict responses instead of model instances."""
        app = APIFlask(__name__)

        @app.get('/users')
        @app.output(list[UserModel])
        def get_users():
            # Return list of dicts - should be validated and serialized
            return [
                {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
                {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
            ]

        with app.test_client() as client:
            response = client.get('/users')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert all('id' in item and 'name' in item and 'email' in item for item in data)

    def test_mixed_list_and_single_endpoints(self):
        """Test that list and single endpoints work correctly together."""
        from typing import List

        app = APIFlask(__name__)

        @app.get('/users')
        @app.output(List[UserModel])
        def list_users():
            return [
                UserModel(id=1, name='Alice', email='alice@example.com'),
                UserModel(id=2, name='Bob', email='bob@example.com'),
            ]

        @app.get('/users/<int:user_id>')
        @app.output(UserModel)
        def get_user(user_id):
            return UserModel(id=user_id, name='Alice', email='alice@example.com')

        @app.post('/users')
        @app.input(UserCreateModel, location='json')
        @app.output(UserModel, status_code=201)
        def create_user(json_data):
            return UserModel(id=1, name=json_data.name, email=json_data.email)

        with app.test_client() as client:
            # Test list endpoint
            response = client.get('/users')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2

            # Test single endpoint
            response = client.get('/users/1')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, dict)
            assert data['id'] == 1

            # Test OpenAPI spec
            rv = client.get('/openapi.json')
            assert rv.status_code == 200
            osv.validate(rv.json)

            spec = rv.get_json()

            # List endpoint should have array schema
            list_schema = spec['paths']['/users']['get']['responses']['200']['content'][
                'application/json'
            ]['schema']
            assert list_schema['type'] == 'array'
            assert list_schema['items']['$ref'] == '#/components/schemas/UserModel'

            # Single endpoint should have object schema
            single_schema = spec['paths']['/users/{user_id}']['get']['responses']['200']['content'][
                'application/json'
            ]['schema']
            assert '$ref' in single_schema
            assert single_schema['$ref'] == '#/components/schemas/UserModel'
            assert 'type' not in single_schema  # Should not be wrapped in array
