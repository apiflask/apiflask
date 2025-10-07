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
