from __future__ import annotations

import typing as t
from io import IOBase

from ..exceptions import _ValidationError
from .base import SchemaAdapter

if t.TYPE_CHECKING:
    from flask import Request

try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    from pydantic.fields import FieldInfo

    HAS_PYDANTIC = True
except ImportError:
    BaseModel = None  # type: ignore
    PydanticValidationError = None  # type: ignore
    FieldInfo = None  # type: ignore
    HAS_PYDANTIC = False


def _format_pydantic_errors(errors: list[dict]) -> dict[str, list[str]]:
    """Format Pydantic validation errors to match marshmallow format.

    Arguments:
        errors: List of Pydantic error dicts

    Returns:
        Dict mapping field names to error message lists
    """
    formatted_errors = {}

    for error in errors:
        # Get the field path
        field_path = '.'.join(str(loc) for loc in error['loc'])
        if not field_path:
            field_path = '_schema'

        # Get the error message
        message = error['msg']

        if field_path not in formatted_errors:
            formatted_errors[field_path] = []
        formatted_errors[field_path].append(message)

    return formatted_errors


class PydanticAdapter(SchemaAdapter):
    """Schema adapter for Pydantic models."""

    def __init__(self, schema: type[BaseModel] | BaseModel) -> None:
        """Initialize the Pydantic adapter.

        Arguments:
            schema: Pydantic model class or instance
        """
        if not HAS_PYDANTIC:
            raise ImportError(
                'Pydantic is required for PydanticAdapter. ' 'Install it with: pip install pydantic'
            )

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            self.model_class = schema
            self.schema = schema
        elif isinstance(schema, BaseModel):
            self.model_class = schema.__class__
            self.schema = schema.__class__
        else:
            raise TypeError(f'Expected Pydantic model, got {type(schema)}')

    @property
    def schema_type(self) -> str:
        return 'pydantic'

    def validate_input(self, request: Request, location: str, **kwargs: t.Any) -> BaseModel:
        """Validate input using Pydantic."""
        try:
            if location == 'json':
                data = request.get_json(force=True)
                if data is None:
                    data = {}
                return self.model_class.model_validate(data)

            elif location == 'query':
                # Handle query parameters
                data = request.args.to_dict()
                return self.model_class.model_validate(data)

            elif location == 'form':
                # Handle form data
                data = request.form.to_dict()
                return self.model_class.model_validate(data)

            elif location == 'files':
                # Handle file uploads with form data
                data = {}
                data.update(request.form.to_dict())

                # Add files to data
                for key, file in request.files.items():
                    if isinstance(file, IOBase):
                        data[key] = file

                return self.model_class.model_validate(data)

            elif location == 'form_and_files':
                # Combine form and files
                data = request.form.to_dict()
                for key, file in request.files.items():
                    data[key] = file
                return self.model_class.model_validate(data)

            elif location == 'json_or_form':
                # Try JSON first, then form
                if request.is_json:
                    data = request.get_json(force=True) or {}
                else:
                    data = request.form.to_dict()
                return self.model_class.model_validate(data)

            else:
                raise ValueError(f'Unsupported location: {location}')

        except PydanticValidationError as error:
            formatted_errors = _format_pydantic_errors(error.errors())
            raise _ValidationError(400, formatted_errors) from error

    def serialize_output(self, data: t.Any, many: bool = False) -> t.Any:
        """Serialize output using Pydantic."""
        if many and isinstance(data, (list, tuple)):
            # Handle lists of data
            result = []
            for item in data:
                if isinstance(item, BaseModel):
                    result.append(item.model_dump())
                elif isinstance(item, dict):
                    try:
                        instance = self.model_class.model_validate(item)
                        result.append(instance.model_dump())
                    except PydanticValidationError:
                        result.append(item)
                else:
                    result.append(item)
            return result
        elif isinstance(data, BaseModel):
            # Pydantic model instance
            return data.model_dump()
        elif isinstance(data, dict):
            # Try to create model instance and serialize
            try:
                instance = self.model_class.model_validate(data)
                return instance.model_dump()
            except PydanticValidationError:
                # If validation fails, return as-is
                return data
        elif isinstance(data, (list, tuple)) and not many:
            # Handle lists when many=False (should serialize individual items)
            result = []
            for item in data:
                if isinstance(item, BaseModel):
                    result.append(item.model_dump())
                elif isinstance(item, dict):
                    try:
                        instance = self.model_class.model_validate(item)
                        result.append(instance.model_dump())
                    except PydanticValidationError:
                        result.append(item)
                else:
                    result.append(item)
            return result
        else:
            # Return as-is for other types
            return data

    def get_openapi_schema(self, **kwargs: t.Any) -> dict[str, t.Any]:
        """Get OpenAPI schema from Pydantic model."""
        try:
            # Use Pydantic's built-in JSON schema generation
            schema = self.model_class.model_json_schema()

            # Convert Pydantic JSON schema to OpenAPI format
            openapi_schema = {}

            if 'type' in schema:
                openapi_schema['type'] = schema['type']

            if 'properties' in schema:
                openapi_schema['properties'] = schema['properties']

            if 'required' in schema:
                openapi_schema['required'] = schema['required']

            if 'title' in schema:
                openapi_schema['title'] = schema['title']

            if 'description' in schema:
                openapi_schema['description'] = schema['description']

            # Handle definitions/references
            if '$defs' in schema:
                openapi_schema['definitions'] = schema['$defs']

            return openapi_schema

        except Exception:
            # Fallback to basic schema
            return {'type': 'object', 'title': self.get_schema_name()}

    def get_schema_name(self) -> str:
        """Get schema name for OpenAPI documentation."""
        return self.model_class.__name__
