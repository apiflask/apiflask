from __future__ import annotations

import typing as t

from .schema_adapters import registry

if t.TYPE_CHECKING:
    pass


class OpenAPIHelper:
    """Helper class for generating OpenAPI schemas from different schema types."""

    def __init__(self) -> None:
        self._marshmallow_plugin = None

    def get_marshmallow_plugin(self):
        """Get or create marshmallow plugin for backwards compatibility."""
        if self._marshmallow_plugin is None:
            try:
                from apispec.ext.marshmallow import MarshmallowPlugin

                self._marshmallow_plugin = MarshmallowPlugin()
            except ImportError:
                pass
        return self._marshmallow_plugin

    def schema_to_spec(self, schema: t.Any) -> dict[str, t.Any]:
        """Convert a schema to OpenAPI specification.

        Arguments:
            schema: Schema object (marshmallow, Pydantic, etc.)

        Returns:
            OpenAPI schema dict
        """
        try:
            adapter = registry.create_adapter(schema)
            return adapter.get_openapi_schema()
        except Exception:
            # Fallback for unknown schema types
            return {'type': 'object'}

    def schema_to_parameters(
        self, schema: t.Any, location: str = 'query'
    ) -> list[dict[str, t.Any]]:
        """Convert schema to OpenAPI parameters.

        Arguments:
            schema: Schema object
            location: Parameter location ('query', 'header', etc.)

        Returns:
            List of OpenAPI parameter definitions
        """
        try:
            adapter = registry.create_adapter(schema)

            # For marshmallow schemas, extract parameters directly from fields
            if adapter.schema_type == 'marshmallow':
                return self._extract_marshmallow_parameters(adapter.schema, location)

            # For other schema types, generate basic parameters
            schema_spec = adapter.get_openapi_schema()
            parameters = []

            if 'properties' in schema_spec:
                required = schema_spec.get('required', [])
                for name, prop_spec in schema_spec['properties'].items():
                    param = {
                        'name': name,
                        'in': location,
                        'required': name in required,
                        'schema': prop_spec,
                    }
                    parameters.append(param)

            return parameters
        except Exception:
            return []

    def _extract_marshmallow_parameters(
        self, schema: t.Any, location: str
    ) -> list[dict[str, t.Any]]:
        """Extract parameters from marshmallow schema fields."""
        parameters = []

        if hasattr(schema, 'fields'):
            for field_name, field in schema.fields.items():
                # Use data_key if available, otherwise use field_name
                param_name = getattr(field, 'data_key', None) or field_name

                field_schema = self._get_field_schema(field)

                # Map location to OpenAPI 'in' field
                openapi_location = location
                if location == 'headers':
                    openapi_location = 'header'

                param = {
                    'name': param_name,
                    'in': openapi_location,
                    'required': getattr(field, 'required', False),
                    'schema': field_schema,
                }

                # For array fields, move style and explode to header level
                if field_schema.get('type') == 'array':
                    if 'style' in field_schema:
                        param['style'] = field_schema.pop('style')
                    if 'explode' in field_schema:
                        param['explode'] = field_schema.pop('explode')

                # Add description from metadata
                if hasattr(field, 'metadata') and field.metadata:
                    description = field.metadata.get('description')
                    if description:
                        param['description'] = description

                parameters.append(param)

        return parameters

    def _get_field_schema(self, field: t.Any) -> dict[str, t.Any]:
        """Get OpenAPI schema for a marshmallow field."""
        field_type = 'string'  # Default
        field_schema = {'type': field_type}

        if hasattr(field, '__class__'):
            field_class_name = field.__class__.__name__.lower()
            if 'integer' in field_class_name or 'int' in field_class_name:
                field_schema['type'] = 'integer'
            elif 'boolean' in field_class_name or 'bool' in field_class_name:
                field_schema['type'] = 'boolean'
            elif (
                'float' in field_class_name
                or 'decimal' in field_class_name
                or 'number' in field_class_name
            ):
                field_schema['type'] = 'number'
            elif 'list' in field_class_name:
                field_schema = {'type': 'array'}
                # For List fields, try to get the inner field type
                if hasattr(field, 'inner') and field.inner:
                    field_schema['items'] = self._get_field_schema(field.inner)
                else:
                    field_schema['items'] = {'type': 'string'}
                # Add array-specific properties for headers
                field_schema['style'] = 'form'
                field_schema['explode'] = True
            elif 'dict' in field_class_name or 'nested' in field_class_name:
                field_schema['type'] = 'object'

        # Check for validators that provide enum values
        if hasattr(field, 'validators') and field.validators:
            for validator in field.validators:
                if hasattr(validator, '__class__') and validator.__class__.__name__ == 'OneOf':
                    if hasattr(validator, 'choices') and validator.choices:
                        field_schema['enum'] = list(validator.choices)
                    break

        return field_schema

    def get_schema_name(self, schema: t.Any) -> str:
        """Get the name for a schema.

        Arguments:
            schema: Schema object

        Returns:
            Schema name string
        """
        try:
            adapter = registry.create_adapter(schema)
            return adapter.get_schema_name()
        except Exception:
            return 'Schema'


# Global helper instance
openapi_helper = OpenAPIHelper()
