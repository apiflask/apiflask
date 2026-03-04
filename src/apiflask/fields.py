# Field aliases were skipped (e.g., Str, Int, Url, etc.)
import typing as t
import warnings

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Annotated
from werkzeug.datastructures import FileStorage

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from flask_marshmallow.fields import AbsoluteURLFor as AbsoluteURLFor
    from flask_marshmallow.fields import Hyperlinks as Hyperlinks
    from flask_marshmallow.fields import URLFor as URLFor
from marshmallow.fields import AwareDateTime as AwareDateTime
from marshmallow.fields import Boolean as Boolean
from marshmallow.fields import Constant as Constant
from marshmallow.fields import Date as Date
from marshmallow.fields import DateTime as DateTime
from marshmallow.fields import Decimal as Decimal
from marshmallow.fields import Dict as Dict
from marshmallow.fields import Email as Email
from marshmallow.fields import Field as Field
from marshmallow.fields import Float as Float
from marshmallow.fields import Function as Function
from marshmallow.fields import Integer as Integer
from marshmallow.fields import IP as IP
from marshmallow.fields import IPv4 as IPv4
from marshmallow.fields import IPv6 as IPv6
from marshmallow.fields import List as List
from marshmallow.fields import Mapping as Mapping
from marshmallow.fields import Method as Method
from marshmallow.fields import NaiveDateTime as NaiveDateTime
from marshmallow.fields import Nested as Nested
from marshmallow.fields import Number as Number
from marshmallow.fields import Pluck as Pluck
from marshmallow.fields import Raw as Raw
from marshmallow.fields import String as String
from marshmallow.fields import Time as Time
from marshmallow.fields import TimeDelta as TimeDelta
from marshmallow.fields import Tuple as Tuple
from marshmallow.fields import URL as URL
from marshmallow.fields import UUID as UUID
from marshmallow.fields import Enum as Enum
from webargs.fields import DelimitedList as DelimitedList
from webargs.fields import DelimitedTuple as DelimitedTuple
from flask_marshmallow.fields import File as File
from flask_marshmallow.fields import Config as Config


class _FileTypeAnnotation:
    """A model for uploaded files.

    *Version Added: 3.1.0*
    """

    @classmethod
    def _validate(cls, __input_value: t.Any, _: t.Any) -> FileStorage:
        if not isinstance(__input_value, FileStorage):
            raise ValueError('Not a valid file.')
        return __input_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_tpye: t.Any, _handler: t.Callable[[t.Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(cls._validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {'type': 'string', 'format': 'binary'}


UploadFile = Annotated[FileStorage, _FileTypeAnnotation]
