import sys
from typing import Any
from typing import Callable
from typing import Dict
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

from flask.wrappers import Response

if TYPE_CHECKING:  # pragma: no cover
    from .schemas import Schema
    from .security import HTTPBasicAuth
    from .security import HTTPTokenAuth


DecoratedType = TypeVar('DecoratedType', bound=Callable[..., Any])
RequestType = TypeVar('RequestType')

_Body = Union[str, bytes, Dict[str, Any], Response]
_Status = Union[str, int]
_Headers = Union[Dict[Any, Any], List[Tuple[Any, Any]]]
ResponseType = Union[
    _Body,
    Tuple[_Body, _Status, _Headers],
    Tuple[_Body, _Status],
    Tuple[_Body, _Headers]
]
SpecCallbackType = Callable[[Union[dict, str]], Union[dict, str]]
ErrorCallbackType = Callable[[int, str, Any, Mapping[str, str]], ResponseType]

SchemaType = Union[Type['Schema'], dict]
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
