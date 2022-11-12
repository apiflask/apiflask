from marshmallow import EXCLUDE

from apiflask import Schema
from apiflask.fields import File
from apiflask.fields import Integer
from apiflask.fields import List
from apiflask.fields import String
from apiflask.validators import OneOf


class Foo(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(dump_default=123)
    name = String(required=True)


class Bar(Schema):
    class Meta:
        unknown = EXCLUDE

    id2 = Integer(dump_default=123)
    name2 = String(required=True)


class Baz(Schema):
    id = Integer(dump_default=123)
    name = String()


class Query(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer(load_default=1)


class Form(Schema):
    name = String()


class Files(Schema):
    image = File()


class FilesList(Schema):
    images = List(File())


class FormAndFiles(Schema):
    name = String()
    image = File()


class EnumPathParameter(Schema):
    image_type = String(validate=OneOf(['jpg', 'png', 'tiff', 'webp']))


class Pagination(Schema):
    class Meta:
        unknown = EXCLUDE

    page = Integer(load_default=1)
    per_page = Integer(load_default=10)


class Header(Schema):
    class Meta:
        unknown = EXCLUDE

    foo = String(load_default='bar')


class ValidationError(Schema):
    status_code = String(required=True)
    message = String(required=True)


class HTTPError(Schema):
    status_code = String(required=True)
    message = String(required=True)
