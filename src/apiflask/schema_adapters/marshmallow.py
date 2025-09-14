from __future__ import annotations

import typing as t

from marshmallow import Schema
from marshmallow import ValidationError as MarshmallowValidationError
from webargs.flaskparser import FlaskParser as BaseFlaskParser
from webargs.multidictproxy import MultiDictProxy

from ..exceptions import _ValidationError
from ..schemas import EmptySchema
from ..schemas import FileSchema
from .base import SchemaAdapter

if t.TYPE_CHECKING:
    from flask import Request


BODY_LOCATIONS = ['json', 'files', 'form', 'form_and_files', 'json_or_form']


class FlaskParser(BaseFlaskParser):
    """Overwrite the default `webargs.FlaskParser.handle_error`.

    Update the default status code and the error description from related
    configuration variables.
    """

    USE_ARGS_POSITIONAL = False

    def handle_error(  # type: ignore
        self,
        error: MarshmallowValidationError,
        req: Request,
        schema: Schema,
        *,
        error_status_code: int,
        error_headers: t.Mapping[str, str],
    ) -> None:
        from flask import current_app

        raise _ValidationError(
            error_status_code or current_app.config['VALIDATION_ERROR_STATUS_CODE'],
            current_app.config['VALIDATION_ERROR_DESCRIPTION'],
            error.messages,
            error_headers,
        )

    def load_location_data(self, *, schema: Schema, req: Request, location: str) -> t.Any:
        return self._load_location_data(schema=schema, req=req, location=location)


parser: FlaskParser = FlaskParser()


@parser.location_loader('form_and_files')
def load_form_and_files(request: Request, schema: t.Any) -> MultiDictProxy:
    return _get_files_and_form(request, schema)


@parser.location_loader('files')
def load_files(request: Request, schema: t.Any) -> MultiDictProxy:
    return _get_files_and_form(request, schema)


def _get_files_and_form(request: Request, schema: t.Any) -> MultiDictProxy:
    """Get files and form data and format field values with schema."""
    form_and_files_data = request.files.copy()
    # Type ignore needed due to MultiDict type incompatibility
    form_and_files_data.update(request.form)  # type: ignore[arg-type]
    return MultiDictProxy(form_and_files_data, schema)


class MarshmallowAdapter(SchemaAdapter):
    """Schema adapter for marshmallow schemas."""

    def __init__(self, schema: Schema | dict | type[Schema]) -> None:
        """Initialize the marshmallow adapter.

        Arguments:
            schema: Marshmallow schema instance, dict, or schema class
        """
        if isinstance(schema, dict):
            # Convert dict schema to marshmallow schema
            from marshmallow import Schema as BaseSchema

            class DictSchema(BaseSchema):
                pass

            for name, field in schema.items():
                setattr(DictSchema, name, field)

            self.schema = DictSchema()
        elif isinstance(schema, type):
            # Check if it's a marshmallow schema class
            try:
                if issubclass(schema, Schema):
                    self.schema = schema()
                else:
                    # If not a marshmallow schema, keep as class (might be Pydantic)
                    self.schema = schema  # type: ignore[unreachable]
            except TypeError:
                # Not a class that can be checked with issubclass
                self.schema = schema
        else:
            self.schema = schema

    @property
    def schema_type(self) -> str:
        return 'marshmallow'

    def validate_input(self, request: Request, location: str, **kwargs: t.Any) -> t.Any:
        """Validate input using marshmallow/webargs."""
        if location == 'files':
            # Handle file uploads with form data
            data = _get_files_and_form(request, self.schema)
            try:
                return self.schema.load(data)
            except MarshmallowValidationError as error:
                raise _ValidationError(400, 'Validation error', error.messages) from error

        # Use webargs for other locations
        return parser.load_location_data(schema=self.schema, req=request, location=location)

    def serialize_output(self, data: t.Any, many: bool = False) -> t.Any:
        """Serialize output using marshmallow."""
        if isinstance(self.schema, (EmptySchema, FileSchema)):
            return data

        # Use marshmallow's dump method which handles dump_default values
        return self.schema.dump(data, many=many)

    def get_openapi_schema(self, **kwargs: t.Any) -> dict[str, t.Any]:
        """Get OpenAPI schema from marshmallow schema."""
        if isinstance(self.schema, EmptySchema):
            return {}
        elif isinstance(self.schema, FileSchema):
            return {'type': self.schema.type, 'format': self.schema.format}

        # For regular marshmallow schemas, use apispec plugin
        try:
            from apispec.ext.marshmallow import MarshmallowPlugin

            plugin = MarshmallowPlugin()
            result: dict[str, t.Any] = plugin.schema_helper(self.schema, **kwargs)  # type: ignore[no-untyped-call]
            return result
        except (ImportError, Exception):
            # Fallback to basic schema generation if apispec not available or fails
            schema_dict: dict[str, t.Any] = {'type': 'object'}

            if hasattr(self.schema, 'fields'):
                properties: dict[str, t.Any] = {}
                required: list[str] = []

                for name, field in self.schema.fields.items():
                    # Check if field is required
                    if hasattr(field, 'required') and field.required:
                        required.append(name)

                    # Basic field type mapping
                    field_type = 'string'  # Default
                    if hasattr(field, '__class__'):
                        field_class_name = field.__class__.__name__.lower()
                        if 'integer' in field_class_name or 'int' in field_class_name:
                            field_type = 'integer'
                        elif 'boolean' in field_class_name or 'bool' in field_class_name:
                            field_type = 'boolean'
                        elif (
                            'float' in field_class_name
                            or 'decimal' in field_class_name
                            or 'number' in field_class_name
                        ):
                            field_type = 'number'
                        elif 'list' in field_class_name:
                            field_type = 'array'
                        elif 'dict' in field_class_name or 'nested' in field_class_name:
                            field_type = 'object'
                        elif field_class_name == 'field':
                            # Generic Field() should be 'object' type
                            field_type = 'object'

                    field_spec = {'type': field_type}

                    # Handle load_default/missing for input validation - avoid marshmallow.missing
                    # First try load_default (newer marshmallow), then fallback to missing
                    if hasattr(field, 'load_default') and field.load_default is not None:
                        from marshmallow import missing

                        if field.load_default is not missing:
                            field_spec['default'] = field.load_default
                    elif hasattr(field, 'missing') and field.missing is not None:
                        from marshmallow import missing

                        if field.missing is not missing:
                            field_spec['default'] = field.missing

                    properties[name] = field_spec

                schema_dict['properties'] = properties
                if required:
                    schema_dict['required'] = required

            return schema_dict

    def get_schema_name(self) -> str:
        """Get schema name for OpenAPI documentation."""
        if hasattr(self.schema, '__class__'):
            return str(self.schema.__class__.__name__)
        return 'Schema'
