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
            assert response.status_code == 400
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

        with app.test_client():
            spec = app.spec
            assert 'components' in spec or 'definitions' in spec
            # Check that the schema is generated
            assert 'paths' in spec
            assert '/users' in spec['paths']

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
            response = client.get('/users?page=2&per_page=20&search=john')
            assert response.status_code == 200
            data = response.get_json()
            assert data['page'] == 2
            assert data['per_page'] == 20
            assert data['search'] == 'john'
