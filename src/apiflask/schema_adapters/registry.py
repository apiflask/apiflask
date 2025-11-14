from __future__ import annotations

import typing as t

from .base import SchemaAdapter

if t.TYPE_CHECKING:
    pass

try:
    from pydantic import BaseModel  # type: ignore[import-not-found]

    HAS_PYDANTIC = True
except ImportError:
    BaseModel = None  # type: ignore
    HAS_PYDANTIC = False

try:
    from marshmallow import Schema

    HAS_MARSHMALLOW = True
except ImportError:
    Schema = None  # type: ignore
    HAS_MARSHMALLOW = False


class SchemaRegistry:
    """Registry for managing schema adapters and automatic type detection.

    *Version added: 3.0.0*
    """

    def __init__(self) -> None:
        self._adapters: dict[str, type[SchemaAdapter]] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """Register the default schema adapters."""
        if HAS_MARSHMALLOW:
            from .marshmallow import MarshmallowAdapter

            self.register('marshmallow', MarshmallowAdapter)

        if HAS_PYDANTIC:
            from .pydantic import PydanticAdapter

            self.register('pydantic', PydanticAdapter)

    def register(self, name: str, adapter_class: type[SchemaAdapter]) -> None:
        """Register a schema adapter.

        Arguments:
            name: Name of the adapter
            adapter_class: Schema adapter class
        """
        self._adapters[name] = adapter_class

    def detect_schema_type(self, schema: t.Any) -> str:
        """Detect the type of schema.

        Arguments:
            schema: Schema object to detect type for

        Returns:
            Schema type name

        Raises:
            ValueError: If schema type cannot be detected
        """
        # Check for Pydantic models first
        if HAS_PYDANTIC:
            try:
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    return 'pydantic'
                elif isinstance(schema, BaseModel):
                    return 'pydantic'
            except TypeError:
                # Not a class that can be checked with issubclass
                pass

        # Check for marshmallow schemas
        if HAS_MARSHMALLOW:
            try:
                if isinstance(schema, Schema):
                    return 'marshmallow'
                elif isinstance(schema, type) and issubclass(schema, Schema):
                    return 'marshmallow'
                elif isinstance(schema, dict):  # Dict schemas are marshmallow
                    return 'marshmallow'
            except TypeError:
                # Not a class that can be checked with issubclass
                pass

        # Check for generic types like list[Model]
        if hasattr(schema, '__origin__') and hasattr(schema, '__args__'):
            # Handle generic types like list[Pet]
            if schema.__origin__ is list and len(schema.__args__) == 1:
                # Detect the inner type
                inner_type = schema.__args__[0]
                return self.detect_schema_type(inner_type)

        # Default to marshmallow for backwards compatibility
        if HAS_MARSHMALLOW:
            return 'marshmallow'

        raise ValueError(f'Cannot detect schema type for {type(schema)}')

    def create_adapter(
        self, schema: t.Any, schema_type: str | None = None, schema_name: str | None = None
    ) -> SchemaAdapter:
        """Create a schema adapter for the given schema.

        Arguments:
            schema: Schema object (can be a model or list[Model]/List[Model])
            schema_type: Optional schema type override
            schema_name: Optional schema name for dict schemas

        Returns:
            Schema adapter instance

        Raises:
            ValueError: If schema type is not supported
        """
        # Check if schema is a list type (list[Model] or List[Model])
        many = False
        inner_schema = schema

        if hasattr(schema, '__origin__') and hasattr(schema, '__args__'):
            if schema.__origin__ is list and len(schema.__args__) == 1:
                # Extract the inner model from list[Model] or List[Model]
                inner_schema = schema.__args__[0]
                many = True

        # Detect schema type from the inner schema
        if schema_type is None:
            schema_type = self.detect_schema_type(inner_schema)

        if schema_type not in self._adapters:
            available = ', '.join(self._adapters.keys())
            raise ValueError(
                f'Unsupported schema type: {schema_type}. ' f'Available types: {available}'
            )

        adapter_class = self._adapters[schema_type]
        return adapter_class(inner_schema, schema_name=schema_name, many=many)

    def get_available_types(self) -> list[str]:
        """Get list of available schema types.

        Returns:
            List of available schema type names
        """
        return list(self._adapters.keys())


# Global registry instance
registry = SchemaRegistry()
