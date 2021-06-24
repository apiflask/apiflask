# Field aliases were skipped (e.g., Str, Int, Url, etc.)
import warnings
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
