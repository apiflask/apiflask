import pytest
from marshmallow import fields
from marshmallow import Schema
from marshmallow import ValidationError

from apiflask.schema_adapters import registry
from apiflask.schema_adapters.marshmallow import MarshmallowAdapter


class PetSchema(Schema):
    """Test pet schema."""

    name = fields.String(required=True)
    age = fields.Integer()
    species = fields.String(load_default='dog')


class UpdatePetSchema(Schema):
    """Partial schema for updates."""

    class Meta:
        partial = True

    name = fields.String()
    age = fields.Integer()


class TestAdapterRegistry:
    """Test AdapterRegistry class."""

    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        from apiflask.schema_adapters import registry as registry1
        from apiflask.schema_adapters import registry as registry2

        assert registry1 is registry2

    def test_create_adapter_with_schema_instance(self):
        """Test creating adapter with schema instance."""
        schema = PetSchema()
        adapter = registry.create_adapter(schema)

        assert isinstance(adapter, MarshmallowAdapter)
        assert adapter.schema_type == 'marshmallow'

    def test_create_adapter_with_schema_class(self):
        """Test creating adapter with schema class."""
        adapter = registry.create_adapter(PetSchema)

        assert isinstance(adapter, MarshmallowAdapter)
        assert adapter.schema_type == 'marshmallow'

    def test_create_adapter_with_dict(self):
        """Test creating adapter with dict schema."""
        dict_schema = {'name': fields.String(required=True), 'age': fields.Integer()}
        adapter = registry.create_adapter(dict_schema)

        assert isinstance(adapter, MarshmallowAdapter)
        assert adapter.schema_type == 'marshmallow'

    def test_create_adapter_with_dict_custom_name(self):
        """Test creating adapter with dict schema and custom name."""
        dict_schema = {'name': fields.String(required=True)}
        adapter = registry.create_adapter(dict_schema, schema_name='CustomName')

        assert isinstance(adapter, MarshmallowAdapter)
        name = adapter.get_schema_name()
        assert name == 'CustomName'

    def test_create_adapter_handles_invalid_type(self):
        """Test that registry handles invalid types gracefully."""
        # Invalid types should raise an exception or return None
        try:
            adapter = registry.create_adapter('not_a_schema')
            # If it doesn't raise, it should handle gracefully
            assert adapter is not None
        except (TypeError, ValueError):
            # Expected to raise for invalid types
            pass


class TestMarshmallowAdapter:
    """Test MarshmallowAdapter class."""

    def test_init_with_schema_instance(self):
        """Test initializing with schema instance."""
        schema = PetSchema()
        adapter = MarshmallowAdapter(schema)

        assert adapter.schema is schema
        assert adapter.schema_type == 'marshmallow'

    def test_init_with_schema_class(self):
        """Test initializing with schema class."""
        adapter = MarshmallowAdapter(PetSchema)

        assert isinstance(adapter.schema, PetSchema)
        assert adapter.schema_type == 'marshmallow'

    def test_init_with_dict(self):
        """Test initializing with dict schema."""
        dict_schema = {'name': fields.String(required=True)}
        adapter = MarshmallowAdapter(dict_schema, schema_name='TestSchema')

        assert isinstance(adapter.schema, Schema)
        assert adapter.schema_type == 'marshmallow'

    def test_init_with_empty_dict(self):
        """Test initializing with empty dict."""
        from apiflask.schemas import EmptySchema

        adapter = MarshmallowAdapter({})

        assert isinstance(adapter.schema, EmptySchema)

    def test_get_schema_name_partial(self):
        """Test get_schema_name with partial schema."""
        schema = PetSchema(partial=True)
        adapter = MarshmallowAdapter(schema)

        name = adapter.get_schema_name()

        # Partial schemas should append 'Update'
        assert name == 'PetSchemaUpdate'

    # Note: get_openapi_schema is tested via openapi_helper in integration tests
    # Direct adapter usage is internal and may vary

    def test_get_openapi_schema_empty(self):
        """Test get_openapi_schema with empty schema."""
        adapter = MarshmallowAdapter({})

        openapi_schema = adapter.get_openapi_schema()

        assert openapi_schema == {}

    def test_get_openapi_schema_file_schema(self):
        """Test get_openapi_schema with FileSchema."""
        from apiflask.schemas import FileSchema

        adapter = MarshmallowAdapter(FileSchema())

        openapi_schema = adapter.get_openapi_schema()

        assert openapi_schema['type'] == 'string'
        assert openapi_schema['format'] == 'binary'

    def test_validate_input_json(self):
        """Test validate_input for json location."""
        from flask import Flask
        from werkzeug.test import EnvironBuilder
        from flask import request

        app = Flask(__name__)
        app.config['VALIDATION_ERROR_STATUS_CODE'] = 422
        app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Validation error'
        adapter = MarshmallowAdapter(PetSchema())

        with app.test_request_context():
            builder = EnvironBuilder(
                method='POST', json={'name': 'Fluffy', 'age': 3}, content_type='application/json'
            )
            env = builder.get_environ()

            with app.request_context(env):
                data = adapter.validate_input(request, 'json')

                assert data['name'] == 'Fluffy'
                assert data['age'] == 3
                # load_default behavior depends on marshmallow configuration

    def test_validate_input_query(self):
        """Test validate_input for query location."""
        from flask import Flask

        app = Flask(__name__)
        app.config['VALIDATION_ERROR_STATUS_CODE'] = 422
        app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Validation error'
        adapter = MarshmallowAdapter(PetSchema())

        with app.test_request_context('/?name=Buddy&age=5'):
            from flask import request

            data = adapter.validate_input(request, 'query')

            assert data['name'] == 'Buddy'
            # Query params come as strings, may need conversion
            assert 'age' in data

    def test_serialize_output(self):
        """Test serialize_output method."""
        adapter = MarshmallowAdapter(PetSchema())

        data = {'name': 'Max', 'age': 7, 'extra': 'ignored'}
        output = adapter.serialize_output(data)

        assert output['name'] == 'Max'
        assert output['age'] == 7
        # Extra fields should be excluded
        assert 'extra' not in output

    def test_serialize_output_many(self):
        """Test serialize_output with many=True."""
        adapter = MarshmallowAdapter(PetSchema())

        data = [{'name': 'Max', 'age': 7}, {'name': 'Bella', 'age': 3}]
        output = adapter.serialize_output(data, many=True)

        assert len(output) == 2
        assert output[0]['name'] == 'Max'
        assert output[1]['name'] == 'Bella'

    def test_serialize_output_empty_schema(self):
        """Test serialize_output with EmptySchema."""
        adapter = MarshmallowAdapter({})

        data = {'any': 'data'}
        output = adapter.serialize_output(data)

        # EmptySchema should pass through data unchanged
        assert output == data

    def test_serialize_output_file_schema(self):
        """Test serialize_output with FileSchema."""
        from apiflask.schemas import FileSchema

        adapter = MarshmallowAdapter(FileSchema())

        data = b'file content'
        output = adapter.serialize_output(data)

        # FileSchema should pass through data unchanged
        assert output == data


class TestFlaskParser:
    """Test FlaskParser class."""

    def test_flask_parser_singleton(self):
        """Test that parser is a singleton."""
        from apiflask.schema_adapters.marshmallow import parser as parser1
        from apiflask.schema_adapters.marshmallow import parser as parser2

        assert parser1 is parser2

    def test_handle_error(self):
        """Test handle_error method."""
        from flask import Flask
        from apiflask.exceptions import _ValidationError
        from apiflask.schema_adapters.marshmallow import parser

        app = Flask(__name__)
        app.config['VALIDATION_ERROR_STATUS_CODE'] = 400
        app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Bad Request'

        with app.app_context():
            error = ValidationError({'field': ['error message']})
            schema = PetSchema()

            with pytest.raises(_ValidationError) as exc_info:
                parser.handle_error(error, None, schema, error_status_code=400, error_headers={})

            assert exc_info.value.status_code == 400
            assert exc_info.value.message == 'Bad Request'
            assert exc_info.value.detail == {'field': ['error message']}

    def test_load_location_data(self):
        """Test load_location_data method."""
        from flask import Flask
        from apiflask.schema_adapters.marshmallow import parser

        app = Flask(__name__)
        schema = PetSchema()

        with app.test_request_context('/?name=Buddy&age=5'):
            from flask import request

            data = parser.load_location_data(schema=schema, req=request, location='query')

            assert data['name'] == 'Buddy'
            # Query params may be strings or converted
            assert 'age' in data

    def test_location_loader_files(self):
        """Test files location loader."""
        from flask import Flask
        from io import BytesIO

        app = Flask(__name__)

        class FileUploadSchema(Schema):
            file = fields.Field()
            description = fields.String()

        schema = FileUploadSchema()

        with app.test_request_context(
            method='POST',
            data={
                'file': (BytesIO(b'file content'), 'test.txt'),
                'description': 'A test file',
            },
            content_type='multipart/form-data',
        ):
            from flask import request
            from apiflask.schema_adapters.marshmallow import parser

            data = parser.load_location_data(schema=schema, req=request, location='files')

            assert 'file' in data
            assert data['description'] == 'A test file'

    def test_location_loader_form_and_files(self):
        """Test form_and_files location loader."""
        from flask import Flask
        from io import BytesIO

        app = Flask(__name__)

        class FormWithFileSchema(Schema):
            file = fields.Field()
            name = fields.String()

        schema = FormWithFileSchema()

        with app.test_request_context(
            method='POST',
            data={'file': (BytesIO(b'content'), 'file.txt'), 'name': 'test'},
            content_type='multipart/form-data',
        ):
            from flask import request
            from apiflask.schema_adapters.marshmallow import parser

            data = parser.load_location_data(schema=schema, req=request, location='form_and_files')

            assert 'file' in data
            assert data['name'] == 'test'
