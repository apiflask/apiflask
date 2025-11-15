from __future__ import annotations

import typing as t

from flask import current_app
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

    *Version added: 3.0.0*
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

    def __init__(
        self,
        schema: Schema | dict | type[Schema],
        schema_name: str | None = None,
        many: bool = False,
    ) -> None:
        """Initialize the marshmallow adapter.

        Arguments:
            schema: Marshmallow schema instance, dict, or schema class
            schema_name: Optional schema name for dict schemas
            many: Whether this schema represents a list/array of items
        """
        if isinstance(schema, dict):
            # Convert dict schema to marshmallow schema
            if schema_name is None:
                schema_name = 'GeneratedSchema'
            if schema == {}:
                self.schema = EmptySchema()
            else:
                self.schema = Schema.from_dict(schema, name=schema_name)()  # type: ignore
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

        self.many = many

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
                raise _ValidationError(
                    current_app.config['VALIDATION_ERROR_STATUS_CODE'],
                    current_app.config['VALIDATION_ERROR_DESCRIPTION'],
                    error.messages,
                ) from error

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

        from apispec.ext.marshmallow import MarshmallowPlugin

        # MarshmallowPlugin expects schema_name_resolver to be None or callable[[type[Schema]], str]
        # Since we don't need custom resolution here, pass None
        plugin = MarshmallowPlugin(schema_name_resolver=None)
        result: dict[str, t.Any] = plugin.schema_helper(self.schema, **kwargs)  # type: ignore[no-untyped-call]
        return result

    def get_schema_name(self) -> str:
        """Get schema name for OpenAPI documentation.

        *Version changed: 3.0.0*

        - Remove "Schema" suffix stripping from schema names.

        """
        schema = self.schema
        if isinstance(schema, type):  # pragma: no cover
            schema = schema()  # type: ignore

        name: str = schema.__class__.__name__
        if hasattr(schema, 'partial') and schema.partial:
            name += 'Update'
        return name
