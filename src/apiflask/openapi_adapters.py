from __future__ import annotations

import typing as t

from .fields import DelimitedList
from .helpers import _normalize_header_name
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
        # The marshmallow converter formats some keywords (e.g. nullable fields)
        # differently for OpenAPI 3.0 and 3.1, so keep one plugin per version.
        self._marshmallow_plugins: dict[str, MarshmallowPlugin | None] = {}

    def get_marshmallow_plugin(self, openapi_version: str) -> MarshmallowPlugin | None:
        """Get or create marshmallow plugin for OpenAPI schema generation.

        Returns a MarshmallowPlugin with initialized converter, ready to use.
        Returns None if marshmallow is not installed.

        Arguments:
            openapi_version: The OpenAPI version the converter
                generates schemas for.

        *Version changed: 3.1.3*

        - Add parameter `openapi_version`, so the generated schemas
          follow the OpenAPI version of the app.
        """
        if openapi_version not in self._marshmallow_plugins:
            plugin: MarshmallowPlugin | None
            try:
                from apispec import APISpec
                from apispec.ext.marshmallow import MarshmallowPlugin

                plugin = MarshmallowPlugin()
                # Initialize the plugin's converter by adding it to an APISpec
                APISpec(
                    title='_temp',
                    version='1.0.0',
                    openapi_version=openapi_version,
                    plugins=[plugin],
                )
                plugin.converter.add_parameter_attribute_function(  # type: ignore
                    self.delimited_list2param
                )
            except ImportError:
                plugin = None
            self._marshmallow_plugins[openapi_version] = plugin

        return self._marshmallow_plugins[openapi_version]

    @staticmethod
    def _get_openapi_version(spec: APISpec | None) -> str:
        """Return the OpenAPI version of the spec, or 3.0.3 without one."""
        return '3.0.3' if spec is None else str(spec.openapi_version)

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

    def schema_to_json_schema(self, schema: t.Any, spec: APISpec | None = None) -> dict[str, t.Any]:
        """Convert a schema to full JSON schema with properties.

        This is different from schema_to_spec in that it returns the complete
        JSON schema definition including all properties, rather than potentially
        returning a reference. Used for base response schemas and other cases
        where the full schema definition is needed.

        Arguments:
            schema: Schema object (marshmallow, Pydantic, etc.)
            spec: The APISpec object, used to generate marshmallow
                schemas for its OpenAPI version. Defaults to 3.0.3
                when omitted.

        Returns:
            Full JSON schema dict with properties

        *Version changed: 3.1.3*

        - Add parameter `spec`, so marshmallow schemas follow the
          OpenAPI version of the app.
        """
        try:
            adapter = registry.create_adapter(schema)

            # For marshmallow schemas, use schema2jsonschema
            if adapter.schema_type == 'marshmallow':
                plugin = self.get_marshmallow_plugin(self._get_openapi_version(spec))
                if plugin is not None:
                    return plugin.converter.schema2jsonschema(adapter.schema)  # type: ignore[union-attr, no-any-return]

            # For other schema types, fall back to get_openapi_schema
            return adapter.get_openapi_schema()
        except Exception:
            # Fallback for unknown schema types
            return {'type': 'object'}

    def schema_to_parameters(
        self, schema: t.Any, location: str = 'query', spec: APISpec | None = None
    ) -> list[dict[str, t.Any]]:
        """Convert schema to OpenAPI parameters.

        Arguments:
            schema: Schema object
            location: Parameter location ('query', 'header', etc.)
            spec: The APISpec object used to register nested schemas
                referenced by the parameters (e.g. Pydantic enums). When
                omitted, nested schemas are not registered.

        Returns:
            List of OpenAPI parameter definitions

        *Version changed: 3.1.2*

        - Add parameter `spec` to register nested schemas referenced by
          the generated parameters.

        *Version changed: 3.1.3*

        - Generate marshmallow parameters for the OpenAPI version of
          `spec`.
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
                parameters = self._extract_marshmallow_parameters(
                    adapter.schema, location=openapi_location, spec=spec
                )

                # Normalize header names
                for param in (p for p in parameters if p.get('in') == 'header'):
                    param['name'] = _normalize_header_name(param['name'])

                return parameters

            # For other schema types, generate basic parameters
            schema_spec = adapter.get_openapi_schema()

            # Pydantic emits nested models (e.g. enums) into `$defs` and points
            # the property schemas at `#/components/schemas/{parent}.{model}`.
            # Register them so those references resolve, the same way body
            # schemas are handled in `APIFlask._register_schema_and_get_ref`.
            # This is limited to Pydantic because the `{parent}.{model}` naming
            # comes from the ref template in `PydanticAdapter.get_openapi_schema`,
            # so it would not match the refs emitted by any other adapter.
            if adapter.schema_type == 'pydantic' and spec is not None:
                nested_defs = extract_pydantic_defs(schema_spec, adapter.get_schema_name())
                for nested_name, nested_schema in nested_defs.items():
                    if nested_name not in spec.components.schemas:
                        spec.components.schema(nested_name, nested_schema)

            parameters = []

            if 'properties' in schema_spec:
                required = schema_spec.get('required', [])
                for name, prop_spec in schema_spec['properties'].items():
                    param = {
                        'name': _normalize_header_name(name)
                        if openapi_location == 'header'
                        else name,
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
        self, schema: t.Any, location: str, spec: APISpec | None = None
    ) -> list[dict[str, t.Any]]:
        """Extract parameters from marshmallow schema fields using apispec converter."""
        plugin = self.get_marshmallow_plugin(self._get_openapi_version(spec))
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
