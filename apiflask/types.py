import sys
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generator
from typing import List
from typing import Mapping
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import TYPE_CHECKING
if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # pragma: no cover
    from typing_extensions import Protocol


if TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response
    from werkzeug.datastructures import Headers
    from wsgiref.types import WSGIApplication
    from .fields import Field
    from .schemas import Schema
    from .security import HTTPBasicAuth
    from .security import HTTPTokenAuth


DecoratedType = TypeVar('DecoratedType', bound=Callable[..., Any])
RequestType = TypeVar('RequestType')

_Body = Union[str, bytes, Dict[str, Any], Generator[str, None, None], 'Response']
_Status = Union[str, int]
_Header = Union[str, List[str], Tuple[str, ...]]
_Headers = Union[Dict[str, _Header], List[Tuple[str, _Header]], 'Headers']
ResponseType = Union[
    _Body,
    Tuple[_Body, _Status],
    Tuple[_Body, _Headers],
    Tuple[_Body, _Status, _Headers],
    'WSGIApplication'
]
SpecCallbackType = Callable[[Union[dict, str]], Union[dict, str]]
ErrorCallbackType = Callable[[int, str, Any, Mapping[str, str]], ResponseType]

DictSchemaType = Dict[str, Union['Field', type]]
SchemaType = Union['Schema', Type['Schema'], DictSchemaType]
HTTPAuthType = Union['HTTPBasicAuth', 'HTTPTokenAuth']
TagsType = Union[List[str], List[Dict[str, Any]]]


class PaginationType(Protocol):
    page: int
    per_page: int
    pages: int
    total: int
    next_num: int
    has_next: bool
    prev_num: int
    has_prev: bool


class ViewFuncType(Protocol):
    _spec: Any
    _method_spec: Any
