from __future__ import annotations

import typing as t

from marshmallow import Schema as BaseSchema
from marshmallow.fields import Integer
from marshmallow.fields import URL
from pydantic import AnyUrl
from pydantic import BaseModel


# schema for the detail object of validation error response
validation_error_detail_schema: dict[str, t.Any] = {
    'type': 'object',
    'properties': {
        '<location>': {
            'type': 'object',
            'properties': {'<field_name>': {'type': 'array', 'items': {'type': 'string'}}},
        }
    },
}


# schema for validation error response
validation_error_schema: dict[str, t.Any] = {
    'properties': {
        'detail': validation_error_detail_schema,
        'message': {'type': 'string'},
    },
    'type': 'object',
}


# schema for generic error response
http_error_schema: dict[str, t.Any] = {
    'properties': {
        'detail': {'type': 'object'},
        'message': {'type': 'string'},
    },
    'type': 'object',
}


class Schema(BaseSchema):
    """A base schema for all schemas. Equivalent to `marshmallow.Schema`.

    *Version Added: 1.2.0*
    """

    pass


class EmptySchema(Schema):
    """An empty schema used to generate empty response/schema.

    *Version changed: 3.0.0*

    - Removed from docs and should only be used internally. Use `{}` instead.
    """

    pass


class PaginationSchema(Schema):
    """A schema for common pagination information."""

    page = Integer()
    per_page = Integer()
    pages = Integer()
    total = Integer()
    current = URL()
    next = URL()
    prev = URL()
    first = URL()
    last = URL()


class PaginationModel(BaseModel):
    """A model for common pagination information."""

    page: int
    per_page: int
    pages: int
    total: int
    current: t.Union[AnyUrl, t.Literal['']]
    next: t.Union[AnyUrl, t.Literal['']]
    prev: t.Union[AnyUrl, t.Literal['']]
    first: t.Union[AnyUrl, t.Literal['']]
    last: t.Union[AnyUrl, t.Literal['']]


class FileSchema(Schema):
    """A schema for file response.

    This is used to represent a file response in OpenAPI spec. If you want to
    embed a file as base64 string in the JSON body, you can use the
    `apiflask.fields.File` field instead.

    Example:

    ```python
    from apiflask.schemas import FileSchema
    from flask import send_from_directory

    @app.get('/images/<filename>')
    @app.output(
        FileSchema(type='string', format='binary'),
        content_type='image/png',
        description='An image file'
    )
    @app.doc(summary="Returns the image file")
    def get_image(filename):
        return send_from_directory(app.config['IMAGE_FOLDER'], filename)
    ```

    The output OpenAPI spec will be:

    ```yaml
    paths:
    /images/{filename}:
      get:
        summary: Returns the image file
        responses:
          '200':
            description: An image file
            content:
              image/png:
                schema:
                  type: string
                  format: binary
    ```

    *Version Added: 2.0.0*
    """

    def __init__(self, *, type: str = 'string', format: str = 'binary') -> None:
        """
        Arguments:
            type: The type of the file. Defaults to `string`.
            format: The format of the file, one of `binary` and `base64`. Defaults to `binary`.
        """
        self.type = type
        self.format = format

    def __repr__(self) -> str:
        return f'schema: \n  type: {self.type}\n  format: {self.format}'
