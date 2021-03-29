from typing import Any, Callable, TypeVar, Union, Dict, List, Tuple, Mapping

from flask.wrappers import Response

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
