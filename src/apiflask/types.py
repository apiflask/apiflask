from __future__ import annotations

import typing as t
from abc import abstractmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import WSGIApplication
    from flask.wrappers import Response
    from werkzeug.datastructures import Headers

    from .exceptions import HTTPError
    from .fields import Field
    from .schemas import Schema
    from .security import (
        APIKeyCookieAuth,
        APIKeyHeaderAuth,
        APIKeyQueryAuth,
        HTTPBasicAuth,
        HTTPTokenAuth,
    )
    from .views import View

    try:
        from pydantic import BaseModel
    except ImportError:
        BaseModel = None  # type: ignore


DecoratedType = t.TypeVar('DecoratedType', bound=t.Callable[..., t.Any])
RequestType = t.TypeVar('RequestType')

ResponseBodyType = t.Union[
    str,
    bytes,
    list[t.Any],
    # Only dict is actually accepted, but Mapping allows for TypedDict.
    t.Mapping[str, t.Any],
    t.Iterator[str],
    t.Iterator[bytes],
    'Response',
]

ResponseStatusType = str | int
_HeaderName = str
_HeaderValue = str | list[str] | tuple[str, ...]
ResponseHeaderType = t.Union[
    dict[_HeaderName, _HeaderValue],
    t.Mapping[_HeaderName, _HeaderValue],
    t.Sequence[tuple[_HeaderName, _HeaderValue]],
    'Headers',
]
ResponseReturnValueType = t.Union[
    ResponseBodyType,
    tuple[ResponseBodyType, ResponseHeaderType],
    tuple[ResponseBodyType, ResponseStatusType],
    tuple[ResponseBodyType, ResponseStatusType, ResponseHeaderType],
    'WSGIApplication',
]
SpecCallbackType = t.Callable[[dict | str], dict | str]
ErrorCallbackType = t.Callable[['HTTPError'], ResponseReturnValueType]

DictSchemaType = dict[str, t.Union['Field', type]]
SchemaType = t.Union['Schema', type['Schema'], DictSchemaType, type['BaseModel']]
OpenAPISchemaType = t.Union['Schema', type['Schema'], dict]
HTTPAuthType = t.Union[
    'HTTPBasicAuth', 'HTTPTokenAuth', 'APIKeyHeaderAuth', 'APIKeyCookieAuth', 'APIKeyQueryAuth'
]
TagsType = list[str] | list[dict[str, t.Any]]
ViewClassType = type['View']
ViewFuncOrClassType = t.Callable | ViewClassType

ResponseObjectType = dict[str, str | dict[str, dict[str, t.Any]]]
ResponsesObjectType = dict[int | str, ResponseObjectType]
ResponsesType = list[int] | dict[int, str] | ResponsesObjectType

RouteCallableType = (
    t.Callable[..., ResponseReturnValueType] | t.Callable[..., t.Awaitable[ResponseReturnValueType]]
)


class PaginationType(t.Protocol):
    page: int
    per_page: int
    pages: int
    total: int
    next_num: int
    has_next: bool
    prev_num: int
    has_prev: bool


class ViewFuncType(t.Protocol):
    _spec: t.Any
    _method_spec: t.Any


@t.runtime_checkable
class SecurityScheme(t.Protocol):
    name: str

    @abstractmethod
    def get_security_scheme(self) -> dict[str, t.Any]:
        """Get security scheme."""

        pass  # pragma: no cover
