from marshmallow import EXCLUDE

from apiflask import Schema
from apiflask.fields import File
from apiflask.fields import Integer
from apiflask.fields import List
from apiflask.fields import String


class FooSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(dump_default=123)
    name = String(required=True)


class BarSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id2 = Integer(dump_default=123)
    name2 = String(required=True)


class BazSchema(Schema):
    id = Integer(dump_default=123)
    name = String()


class QuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(load_default=1)


class FormSchema(Schema):
    name = String()


class FilesSchema(Schema):
    image = File()


class FilesListSchema(Schema):
    images = List(File())


class FormAndFilesSchema(Schema):
    name = String()
    image = File()


class PaginationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = Integer(load_default=1)
    per_page = Integer(load_default=10)


class HeaderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    foo = String(load_default='bar')


class ValidationErrorSchema(Schema):
    status_code = String(required=True)
    message = String(required=True)


class HTTPErrorSchema(Schema):
    status_code = String(required=True)
    message = String(required=True)
