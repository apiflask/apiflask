import pytest
from marshmallow import Schema, fields, validate

from apiflask.openapi_adapters import OpenAPIHelper, get_unique_schema_name

from .schemas import NullableFieldSchema


class SimpleSchema(Schema):
    """Simple test schema."""

    name = fields.String(required=True)
    age = fields.Integer()


class EnumSchema(Schema):
    """Schema with enum field."""

    status = fields.String(validate=validate.OneOf(['active', 'inactive']))


class NestedSchema(Schema):
    """Schema with nested field."""

    user = fields.Nested(SimpleSchema)
    tags = fields.List(fields.String())


def test_get_unique_schema_name():
    """Test get_unique_schema_name function."""
    from apispec import APISpec
    from apispec.ext.marshmallow import MarshmallowPlugin

    plugin = MarshmallowPlugin()
    spec = APISpec(title='Test', version='1.0.0', openapi_version='3.1.0', plugins=[plugin])

    # Register a schema
    spec.components.schema('TestSchema', schema=SimpleSchema())

    # Get unique name for conflicting schema
    unique_name = get_unique_schema_name(spec, 'TestSchema')
    assert unique_name == 'TestSchema1'

    # Register the unique name
    spec.components.schema(unique_name, schema=SimpleSchema())

    # Get another unique name
    unique_name2 = get_unique_schema_name(spec, 'TestSchema')
    assert unique_name2 == 'TestSchema2'


class TestOpenAPIHelper:
    """Test OpenAPIHelper class."""

    def test_get_marshmallow_plugin(self):
        """Test get_marshmallow_plugin method."""
        helper = OpenAPIHelper('3.1.0')
        plugin = helper.get_marshmallow_plugin()

        assert plugin is not None
        assert hasattr(plugin, 'converter')
        assert plugin.converter is not None

    def test_get_marshmallow_plugin_caching(self):
        """Test that marshmallow plugin is cached."""
        helper = OpenAPIHelper('3.1.0')
        plugin1 = helper.get_marshmallow_plugin()
        plugin2 = helper.get_marshmallow_plugin()

        assert plugin1 is plugin2

    def test_schema_to_spec_marshmallow(self):
        """Test schema_to_spec with marshmallow schema."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        spec = helper.schema_to_spec(schema)

        # schema_to_spec returns minimal spec (type only)
        # For full spec with properties, use schema_to_json_schema
        assert spec['type'] == 'object'

    def test_schema_to_spec_dict(self):
        """Test schema_to_spec with dict schema."""
        helper = OpenAPIHelper('3.1.0')
        schema = {'name': fields.String(required=True)}

        spec = helper.schema_to_spec(schema)

        # Dict schemas are converted to marshmallow schemas by the adapter
        assert spec['type'] == 'object'

    def test_schema_to_json_schema_marshmallow(self):
        """Test schema_to_json_schema with marshmallow schema."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        json_schema = helper.schema_to_json_schema(schema)

        assert json_schema['type'] == 'object'
        assert 'properties' in json_schema
        assert 'name' in json_schema['properties']
        assert json_schema['properties']['name']['type'] == 'string'
        assert 'age' in json_schema['properties']
        assert json_schema['properties']['age']['type'] == 'integer'

    @pytest.mark.parametrize(
        'openapi_version, expected',
        [
            ('3.0.0', {'type': 'string', 'nullable': True}),
            ('3.1.0', {'type': ['string', 'null']}),
        ],
    )
    def test_nullable_field_with_openapi_version(self, openapi_version, expected):
        """Test that nullable fields follow the configured OpenAPI version."""
        helper = OpenAPIHelper(openapi_version)
        schema = NullableFieldSchema()

        json_schema = helper.schema_to_json_schema(schema)
        assert json_schema['properties']['name'] == expected

        parameters = helper.schema_to_parameters(schema, location='query')
        assert parameters[0]['schema'] == expected

    def test_schema_to_parameters_query(self):
        """Test schema_to_parameters for query parameters."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        params = helper.schema_to_parameters(schema, location='query')

        assert len(params) == 2
        assert params[0]['name'] == 'name'
        assert params[0]['in'] == 'query'
        assert params[0]['required'] is True
        assert params[0]['schema']['type'] == 'string'

        assert params[1]['name'] == 'age'
        assert params[1]['in'] == 'query'
        assert params[1]['required'] is False

    def test_schema_to_parameters_headers(self):
        """Test schema_to_parameters for headers."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        params = helper.schema_to_parameters(schema, location='headers')

        assert len(params) == 2
        assert all(p['in'] == 'header' for p in params)

    def test_schema_to_parameters_path(self):
        """Test schema_to_parameters for path parameters."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        params = helper.schema_to_parameters(schema, location='view_args')

        assert len(params) == 2
        assert all(p['in'] == 'path' for p in params)

    def test_schema_to_parameters_with_enum(self):
        """Test schema_to_parameters handles enum validation."""
        helper = OpenAPIHelper('3.1.0')
        schema = EnumSchema()

        params = helper.schema_to_parameters(schema, location='query')

        assert len(params) == 1
        assert params[0]['schema']['type'] == 'string'
        assert 'enum' in params[0]['schema']
        assert params[0]['schema']['enum'] == ['active', 'inactive']

    def test_schema_to_parameters_location_mapping(self):
        """Test schema_to_parameters location mapping."""
        helper = OpenAPIHelper('3.1.0')
        schema = SimpleSchema()

        # Test various location mappings
        locations = {
            'query': 'query',
            'querystring': 'query',
            'headers': 'header',
            'view_args': 'path',
            'cookies': 'cookie',
        }

        for input_loc, expected_loc in locations.items():
            params = helper.schema_to_parameters(schema, location=input_loc)
            assert all(p['in'] == expected_loc for p in params)

    def test_get_schema_name_dict(self):
        """Test get_schema_name with dict schema."""
        helper = OpenAPIHelper('3.1.0')
        schema = {'name': fields.String()}

        name = helper.get_schema_name(schema)

        # Dict schemas get 'Generated' prefix
        assert name == 'GeneratedSchema'

    def test_schema_to_spec_unknown_type(self):
        """Test schema_to_spec with unknown schema type."""
        helper = OpenAPIHelper('3.1.0')

        # Pass something that's not a valid schema
        spec = helper.schema_to_spec('not_a_schema')

        # Should return fallback
        assert spec == {'type': 'object'}

    def test_schema_to_json_schema_unknown_type(self):
        """Test schema_to_json_schema with unknown schema type."""
        helper = OpenAPIHelper('3.1.0')

        # Pass something that's not a valid schema
        json_schema = helper.schema_to_json_schema('not_a_schema')

        # Should return fallback
        assert json_schema == {'type': 'object'}

    def test_schema_to_parameters_unknown_type(self):
        """Test schema_to_parameters with unknown schema type."""
        helper = OpenAPIHelper('3.1.0')

        # Pass something that's not a valid schema
        params = helper.schema_to_parameters('not_a_schema', location='query')

        # Should return empty list
        assert params == []

    def test_schema_to_parameters_registers_nested_schemas_with_spec(self):
        """Test schema_to_parameters registers nested schemas when spec is provided."""
        from apispec import APISpec
        from apispec.ext.marshmallow import MarshmallowPlugin

        plugin = MarshmallowPlugin()
        spec = APISpec(title='Test', version='1.0.0', openapi_version='3.1.0', plugins=[plugin])
        helper = OpenAPIHelper('3.1.0')

        params = helper.schema_to_parameters(NestedSchema, location='query', spec=spec)
        assert len(params) == 2
        assert 'Simple' in spec.components.schemas

    def test_schema_to_json_schema_registers_nested_schemas_with_spec(self):
        """Test schema_to_json_schema registers nested schemas when spec is provided."""
        from apispec import APISpec
        from apispec.ext.marshmallow import MarshmallowPlugin

        plugin = MarshmallowPlugin()
        spec = APISpec(title='Test', version='1.0.0', openapi_version='3.1.0', plugins=[plugin])
        helper = OpenAPIHelper('3.1.0')

        json_schema = helper.schema_to_json_schema(NestedSchema, spec=spec)
        assert 'properties' in json_schema
        assert 'Simple' in spec.components.schemas
