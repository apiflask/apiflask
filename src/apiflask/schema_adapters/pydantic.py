from __future__ import annotations

import typing as t

from flask import current_app
from werkzeug.datastructures import FileStorage

from ..exceptions import _ValidationError
from ..fields import UploadFile
from ..helpers import _get_fields_by_type
from .base import SchemaAdapter

if t.TYPE_CHECKING:
    from flask import Request

try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    from pydantic.fields import FieldInfo
    from pydantic_core import ErrorDetails

    HAS_PYDANTIC = True
except ImportError:
    BaseModel = None  # type: ignore
    PydanticValidationError = None  # type: ignore
    FieldInfo = None  # type: ignore
    ErrorDetails = None  # type: ignore
    HAS_PYDANTIC = False


def _format_pydantic_errors(errors: list[ErrorDetails]) -> dict[str, list[str]]:
    """Format Pydantic validation errors to match marshmallow format.

    Arguments:
        errors: List of Pydantic error dicts

    Returns:
        Dict mapping field names to error message lists
    """
    formatted_errors: dict[str, list[str]] = {}

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

    def __init__(
        self,
        schema: type[BaseModel] | BaseModel,
        schema_name: str | None = None,
        many: bool = False,
    ) -> None:
        """Initialize the Pydantic adapter.

        Arguments:
            schema: Pydantic model class or instance
            schema_name: Optional schema name (not used for Pydantic)
            many: Whether this schema represents a list/array of items
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

        self.many = many

    @property
    def schema_type(self) -> str:
        return 'pydantic'

    @staticmethod
    def handle_files(
        request: Request, data: dict, file_fields: t.List[str], file_list_fields: t.List[str]
    ) -> None:
        for key in file_fields:
            fs = request.files.get(key)
            if fs:
                data[key] = fs
            else:
                value = request.values.get(key)
                # handle empty value sent by swagger ui
                if isinstance(value, t.Sequence) and len(value) == 0:
                    data[key] = None
                else:
                    data[key] = value

        for key in file_list_fields:
            if key in request.files.keys():
                data[key] = request.files.getlist(key)
            else:
                value = request.values.get(key)
                # handle empty value sent by swagger ui
                if isinstance(value, t.Sequence) and (len(value) == 0 or value == 'null'):
                    data[key] = None
                else:
                    data[key] = value

    def validate_input(self, request: Request, location: str, **kwargs: t.Any) -> BaseModel:
        """Validate input using Pydantic."""
        try:
            if location == 'json':
                data = request.get_json(force=True)
                if data is None:
                    data = {}
                return self.model_class.model_validate(data)

            elif location == 'query' or location == 'querystring':
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

                file_fields = _get_fields_by_type(
                    self.model_class, UploadFile
                ) + _get_fields_by_type(self.model_class, FileStorage)
                file_list_fields = _get_fields_by_type(self.model_class, t.List[UploadFile])

                # Add files to data
                self.handle_files(request, data, file_fields, file_list_fields)

                return self.model_class.model_validate(data)

            elif location == 'form_and_files':
                # Combine form and files
                data = request.form.to_dict()

                file_fields = _get_fields_by_type(
                    self.model_class, UploadFile
                ) + _get_fields_by_type(self.model_class, FileStorage)
                file_list_fields = _get_fields_by_type(self.model_class, t.List[UploadFile])

                # Add files to data
                self.handle_files(request, data, file_fields, file_list_fields)

                return self.model_class.model_validate(data)

            elif location == 'json_or_form':
                # Try JSON first, then form
                if request.is_json:
                    data = request.get_json(force=True) or {}
                else:
                    data = request.form.to_dict()
                return self.model_class.model_validate(data)

            elif location == 'cookies':
                # Handle cookies
                data = request.cookies.to_dict()
                return self.model_class.model_validate(data)

            elif location == 'headers':
                # Handle headers - convert header names to field names
                # HTTP headers like X-Token become x_token for Pydantic fields
                data = {}
                for header_name, value in request.headers:
                    # Convert header name to field name (e.g., X-Token -> x_token)
                    field_name = header_name.lower().replace('-', '_')
                    data[field_name] = value
                return self.model_class.model_validate(data)

            elif location == 'path' or location == 'view_args':
                # Handle path/view_args
                data = request.view_args or {}
                return self.model_class.model_validate(data)

            else:
                raise ValueError(f'Unsupported location: {location}')

        except PydanticValidationError as error:
            formatted_errors = _format_pydantic_errors(error.errors())
            raise _ValidationError(
                current_app.config['VALIDATION_ERROR_STATUS_CODE'],
                current_app.config['VALIDATION_ERROR_DESCRIPTION'],
                {location: formatted_errors},
            ) from error

    def serialize_output(self, data: t.Any, many: bool = False) -> t.Any:
        """Serialize output using Pydantic with validation."""
        if many and isinstance(data, (list, tuple)):
            # Handle lists of data
            result = []
            for item in data:
                if isinstance(item, BaseModel):
                    # Already validated, just serialize
                    result.append(item.model_dump(mode='json', by_alias=True))
                else:
                    # Validate and serialize
                    validated = self.model_class.model_validate(item)
                    result.append(validated.model_dump(mode='json', by_alias=True))
            return result
        elif isinstance(data, BaseModel):
            # Pydantic model instance - already validated, just serialize
            return data.model_dump(mode='json', by_alias=True)
        elif isinstance(data, (list, tuple)) and not many:
            # Handle lists when many=False
            result = []
            for item in data:
                if isinstance(item, BaseModel):
                    result.append(item.model_dump(mode='json', by_alias=True))
                else:
                    # Validate and serialize
                    validated = self.model_class.model_validate(item)
                    result.append(validated.model_dump(mode='json', by_alias=True))
            return result
        else:
            # Validate and serialize (dicts, primitives)
            validated = self.model_class.model_validate(data)
            return validated.model_dump(mode='json', by_alias=True)

    def get_openapi_schema(self, **kwargs: t.Any) -> dict[str, t.Any]:
        """Get OpenAPI schema from Pydantic model.

        Uses Pydantic's ref_template to generate OpenAPI-compliant $ref paths.
        Nested models in $defs should be extracted and registered separately
        at the components/schemas level.
        """
        try:
            # Generate schema name for use in ref_template
            schema_name = self.get_schema_name()

            # Use ref_template to make Pydantic generate OpenAPI-compatible refs
            # The {model} placeholder will be replaced with nested model names
            ref_template = f'#/components/schemas/{schema_name}.{{model}}'

            # Generate JSON schema with OpenAPI-compatible references
            schema = self.model_class.model_json_schema(
                ref_template=ref_template, mode=kwargs.get('mode', 'validation')
            )

            # Note: The $defs should be extracted and registered separately
            # in components/schemas. The caller (app.py) should handle this.

            return schema

        except Exception:
            # Fallback to basic schema
            return {'type': 'object', 'title': self.get_schema_name()}

    def get_schema_name(self) -> str:
        """Get schema name for OpenAPI documentation."""
        return self.model_class.__name__
