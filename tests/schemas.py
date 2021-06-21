from marshmallow import EXCLUDE

from apiflask import Schema
from apiflask.fields import Integer
from apiflask.fields import String


class FooSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(default=123)
    name = String(required=True)


class BarSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id2 = Integer(default=123)
    name2 = String(required=True)


class BazSchema(Schema):
    id = Integer(default=123)
    name = String()


class QuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(missing=1)


class PaginationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = Integer(missing=1)
    per_page = Integer(missing=10)


class HeaderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    foo = String(missing='bar')


class ValidationErrorSchema(Schema):
    status_code = String(required=True)
    message = String(required=True)


class HTTPErrorSchema(Schema):
    status_code = String(required=True)
    message = String(required=True)
