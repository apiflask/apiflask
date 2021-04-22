from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Mapping
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from flask.wrappers import Response

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

SchemaType = Union[Type[Schema], dict]
HTTPAuthType = Union[HTTPBasicAuth, HTTPTokenAuth]
TagsType = Union[List[str], List[Dict[str, Any]]]
