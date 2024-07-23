from __future__ import annotations

import typing as t
from typing import Protocol

if t.TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401
    from _typeshed.wsgi import WSGIApplication  # noqa: F401
    from .fields import Field  # noqa: F401
    from .schemas import Schema  # noqa: F401
    from .security import HTTPBasicAuth  # noqa: F401
    from .security import HTTPTokenAuth  # noqa: F401
    from .exceptions import HTTPError  # noqa: F401
    from .views import View  # noqa: F401


DecoratedType = t.TypeVar('DecoratedType', bound=t.Callable[..., t.Any])
RequestType = t.TypeVar('RequestType')

ResponseBodyType = t.Union[
    str,
    bytes,
    t.List[t.Any],
    # Only dict is actually accepted, but Mapping allows for TypedDict.
    t.Mapping[str, t.Any],
    t.Iterator[str],
    t.Iterator[bytes],
    'Response',
]

ResponseStatusType = t.Union[str, int]
_HeaderName = str
_HeaderValue = t.Union[str, t.List[str], t.Tuple[str, ...]]
ResponseHeaderType = t.Union[
    t.Dict[_HeaderName, _HeaderValue],
    t.Mapping[_HeaderName, _HeaderValue],
    t.Sequence[t.Tuple[_HeaderName, _HeaderValue]],
    'Headers',
]
ResponseReturnValueType = t.Union[
    ResponseBodyType,
    t.Tuple[ResponseBodyType, ResponseHeaderType],
    t.Tuple[ResponseBodyType, ResponseStatusType],
    t.Tuple[ResponseBodyType, ResponseStatusType, ResponseHeaderType],
    'WSGIApplication',
]
SpecCallbackType = t.Callable[[t.Union[dict, str]], t.Union[dict, str]]
ErrorCallbackType = t.Callable[['HTTPError'], ResponseReturnValueType]

DictSchemaType = t.Dict[str, t.Union['Field', type]]
SchemaType = t.Union['Schema', t.Type['Schema'], DictSchemaType]
OpenAPISchemaType = t.Union['Schema', t.Type['Schema'], dict]
HTTPAuthType = t.Union['HTTPBasicAuth', 'HTTPTokenAuth']
TagsType = t.Union[t.List[str], t.List[t.Dict[str, t.Any]]]
ViewClassType = t.Type['View']
ViewFuncOrClassType = t.Union[t.Callable, ViewClassType]

ResponseObjectType = t.Dict[str, t.Union[str, t.Dict[str, t.Dict[str, t.Any]]]]
ResponsesObjectType = t.Dict[t.Union[int, str], ResponseObjectType]
ResponsesType = t.Union[t.List[int], t.Dict[int, str], ResponsesObjectType]

RouteCallableType = t.Union[
    t.Callable[..., ResponseReturnValueType],
    t.Callable[..., t.Awaitable[ResponseReturnValueType]],
]


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
