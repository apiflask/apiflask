import sys
import typing as t

if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # pragma: no cover
    from typing_extensions import Protocol

if t.TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401
    from wsgiref.types import WSGIApplication  # noqa: F401
    from .fields import Field  # noqa: F401
    from .schemas import Schema  # noqa: F401
    from .security import HTTPBasicAuth  # noqa: F401
    from .security import HTTPTokenAuth  # noqa: F401
    from .exceptions import HTTPError  # noqa: F401


DecoratedType = t.TypeVar('DecoratedType', bound=t.Callable[..., t.Any])
RequestType = t.TypeVar('RequestType')

_Body = t.Union[str, bytes, t.Dict[str, t.Any], t.Generator[str, None, None], 'Response']
_Status = t.Union[str, int]
_Header = t.Union[str, t.List[str], t.Tuple[str, ...]]
_Headers = t.Union[t.Dict[str, _Header], t.List[t.Tuple[str, _Header]], 'Headers']
ResponseType = t.Union[
    _Body,
    t.Tuple[_Body, _Status],
    t.Tuple[_Body, _Headers],
    t.Tuple[_Body, _Status, _Headers],
    'WSGIApplication'
]
SpecCallbackType = t.Callable[[t.Union[dict, str]], t.Union[dict, str]]
ErrorCallbackType = t.Callable[['HTTPError'], ResponseType]

DictSchemaType = t.Dict[str, t.Union['Field', type]]
SchemaType = t.Union['Schema', t.Type['Schema'], DictSchemaType]
OpenAPISchemaType = t.Union['Schema', t.Type['Schema'], dict]
HTTPAuthType = t.Union['HTTPBasicAuth', 'HTTPTokenAuth']
TagsType = t.Union[t.List[str], t.List[t.Dict[str, t.Any]]]


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
    _spec: t.Any
    _method_spec: t.Any
