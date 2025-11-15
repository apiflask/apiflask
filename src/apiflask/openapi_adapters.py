from __future__ import annotations

import typing as t

from .fields import DelimitedList
from .schema_adapters import registry

if t.TYPE_CHECKING:
    from apispec import APISpec
    from apispec.ext.marshmallow import MarshmallowPlugin


def get_unique_schema_name(spec: APISpec, base_name: str) -> str:
    """Generate a unique schema name by appending a counter.

    Arguments:
        spec: The APISpec object
        base_name: The base schema name

    Returns:
        A unique schema name that doesn't exist in spec.components.schemas
    """
    counter = 1
    schema_name = base_name
    while schema_name in spec.components.schemas:
        schema_name = f'{base_name}{counter}'
        counter += 1
    return schema_name


def extract_pydantic_defs(schema_dict: dict[str, t.Any], parent_name: str) -> dict[str, t.Any]:
    """Extract $defs from Pydantic schema and return them with composed keys.

    Arguments:
        schema_dict: Schema dictionary from Pydantic model_json_schema()
        parent_name: Parent schema name for composing nested schema names

    Returns:
        Dictionary of extracted definitions with composed keys like "ParentName.ChildName"
    """
    definitions = {}

    if '$defs' in schema_dict:
        for def_name, def_schema in schema_dict['$defs'].items():
            composed_key = f'{parent_name}.{def_name}'
            definitions[composed_key] = def_schema

        # Remove $defs from the original schema
        del schema_dict['$defs']

    return definitions


class OpenAPIHelper:
    """Helper class for generating OpenAPI schemas from different schema types.

    *Version added: 3.0.0*
    """

    def __init__(self) -> None:
        self._marshmallow_plugin: MarshmallowPlugin | None = None
        self._marshmallow_plugin_initialized = False

    def get_marshmallow_plugin(self) -> MarshmallowPlugin | None:
        """Get or create marshmallow plugin for OpenAPI schema generation.

        Returns a MarshmallowPlugin with initialized converter, ready to use.
        Returns None if marshmallow is not installed.
        """
        if not self._marshmallow_plugin_initialized:
            try:
                from apispec import APISpec
                from apispec.ext.marshmallow import MarshmallowPlugin

                self._marshmallow_plugin = MarshmallowPlugin()
                # Initialize the plugin's converter by adding it to an APISpec
                APISpec(
                    title='_temp',
                    version='1.0.0',
                    openapi_version='3.0.3',
                    plugins=[self._marshmallow_plugin],
                )
                self._marshmallow_plugin.converter.add_parameter_attribute_function(  # type: ignore
                    self.delimited_list2param
                )

            except ImportError:
                self._marshmallow_plugin = None
            finally:
                self._marshmallow_plugin_initialized = True

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

    def schema_to_json_schema(self, schema: t.Any) -> dict[str, t.Any]:
        """Convert a schema to full JSON schema with properties.

        This is different from schema_to_spec in that it returns the complete
        JSON schema definition including all properties, rather than potentially
        returning a reference. Used for base response schemas and other cases
        where the full schema definition is needed.

        Arguments:
            schema: Schema object (marshmallow, Pydantic, etc.)

        Returns:
            Full JSON schema dict with properties
        """
        try:
            adapter = registry.create_adapter(schema)

            # For marshmallow schemas, use schema2jsonschema
            if adapter.schema_type == 'marshmallow':
                plugin = self.get_marshmallow_plugin()
                if plugin is not None:
                    return plugin.converter.schema2jsonschema(adapter.schema)  # type: ignore[union-attr, no-any-return]

            # For other schema types, fall back to get_openapi_schema
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

            # Map location to OpenAPI 'in' field
            openapi_location = location
            if location == 'headers':
                openapi_location = 'header'
            elif location == 'view_args':
                openapi_location = 'path'
            elif location == 'querystring':
                openapi_location = 'query'
            elif location == 'cookies':
                openapi_location = 'cookie'

            # For marshmallow schemas, extract parameters directly from fields
            if adapter.schema_type == 'marshmallow':
                return self._extract_marshmallow_parameters(
                    adapter.schema, location=openapi_location
                )

            # For other schema types, generate basic parameters
            schema_spec = adapter.get_openapi_schema()
            parameters = []

            if 'properties' in schema_spec:
                required = schema_spec.get('required', [])
                for name, prop_spec in schema_spec['properties'].items():
                    param = {
                        'name': name,
                        'in': openapi_location,
                        'required': name in required,
                        'schema': prop_spec,
                    }
                    parameters.append(param)

            return parameters
        except Exception:
            return []

    def delimited_list2param(self, field, **kwargs) -> dict:  # type: ignore[no-untyped-def]
        """Set correct OpenAPI parameter attributes for DelimitedList fields."""
        ret: dict = {}
        if isinstance(field, DelimitedList):
            ret['explode'] = False
            ret['style'] = 'form'
        return ret

    def _extract_marshmallow_parameters(
        self, schema: t.Any, location: str
    ) -> list[dict[str, t.Any]]:
        """Extract parameters from marshmallow schema fields using apispec converter."""
        plugin = self.get_marshmallow_plugin()
        if plugin is None:
            return []

        return plugin.converter.schema2parameters(schema, location=location)  # type: ignore[union-attr, no-any-return]

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
