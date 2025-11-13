from __future__ import annotations

import typing as t
from abc import ABC
from abc import abstractmethod

if t.TYPE_CHECKING:
    from flask import Request


class SchemaAdapter(ABC):
    """Base class for schema adapters.

    Schema adapters provide a common interface for different schema libraries
    (marshmallow, Pydantic, etc.) to integrate with APIFlask.

    *Version added: 3.0.0*
    """

    def __init__(self, schema: t.Any, schema_name: str | None = None, many: bool = False) -> None:
        """Initialize the adapter with a schema.

        Arguments:
            schema: The schema object (marshmallow Schema, Pydantic model, etc.)
            schema_name: Optional schema name (used by some adapters like marshmallow)
            many: Whether this schema represents a list/array of items
        """
        self.schema = schema
        self.many = many

    @abstractmethod
    def validate_input(self, request: Request, location: str, **kwargs: t.Any) -> t.Any:
        """Validate and parse input data from request.

        Arguments:
            request: Flask request object
            location: Location of data ('json', 'query', 'form', etc.)
            **kwargs: Additional arguments passed from decorator

        Returns:
            Validated and parsed data

        Raises:
            ValidationError: If validation fails
        """
        ...

    @abstractmethod
    def serialize_output(self, data: t.Any, many: bool = False) -> t.Any:
        """Serialize output data.

        Arguments:
            data: Data to serialize
            many: Whether to serialize many objects

        Returns:
            Serialized data ready for JSON response
        """
        ...

    @abstractmethod
    def get_openapi_schema(self, **kwargs: t.Any) -> dict[str, t.Any]:
        """Get OpenAPI schema definition.

        Arguments:
            **kwargs: Additional arguments for schema generation

        Returns:
            OpenAPI schema dict
        """
        ...

    @abstractmethod
    def get_schema_name(self) -> str:
        """Get the name of the schema for OpenAPI documentation.

        Returns:
            Schema name string
        """
        ...

    @property
    @abstractmethod
    def schema_type(self) -> str:
        """Get the type of schema adapter.

        Returns:
            Schema type identifier ('marshmallow', 'pydantic', etc.)
        """
        ...
