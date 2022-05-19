import typing as t

from marshmallow import Schema as Schema
from marshmallow.fields import Integer
from marshmallow.fields import URL


# schema for the detail object of validation error response
validation_error_detail_schema: t.Dict[str, t.Any] = {
    'type': 'object',
    'properties': {
        '<location>': {
            'type': 'object',
            'properties': {
                '<field_name>': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                }
            }
        }
    }
}


# schema for validation error response
validation_error_schema: t.Dict[str, t.Any] = {
    'properties': {
        'detail': validation_error_detail_schema,
        'message': {
            'type': 'string'
        },
    },
    'type': 'object'
}


# schema for generic error response
http_error_schema: t.Dict[str, t.Any] = {
    'properties': {
        'detail': {
            'type': 'object'
        },
        'message': {
            'type': 'string'
        },
    },
    'type': 'object'
}


class EmptySchema(Schema):
    """An empty schema used to generate a 204 response.

    Example:

    ```python
    @app.delete('/foo')
    @app.output(EmptySchema)
    def delete_foo():
        return ''
    ```

    It equals to:

    ```python
    @app.delete('/foo')
    @app.output({}, 204)
    def delete_foo():
        return ''
    ```
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
