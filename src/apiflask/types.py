from __future__ import annotations

import typing as t
from abc import abstractmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import WSGIApplication  # noqa: F401
    from flask.wrappers import Response  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401

    from .exceptions import HTTPError  # noqa: F401
    from .fields import Field  # noqa: F401
    from .schemas import Schema  # noqa: F401
    from .security import (
        APIKeyCookieAuth,  # noqa: F401
        APIKeyHeaderAuth,  # noqa: F401
        APIKeyQueryAuth,  # noqa: F401
        HTTPBasicAuth,  # noqa: F401
        HTTPTokenAuth,  # noqa: F401
    )
    from .views import View  # noqa: F401

    try:
        from pydantic import BaseModel  # noqa: F401
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

ResponseStatusType = t.Union[str, int]
_HeaderName = str
_HeaderValue = t.Union[str, list[str], tuple[str, ...]]
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
SpecCallbackType = t.Callable[[t.Union[dict, str]], t.Union[dict, str]]
ErrorCallbackType = t.Callable[['HTTPError'], ResponseReturnValueType]

DictSchemaType = dict[str, t.Union['Field', type]]
SchemaType = t.Union['Schema', type['Schema'], DictSchemaType, type['BaseModel']]
OpenAPISchemaType = t.Union['Schema', type['Schema'], dict]
HTTPAuthType = t.Union[
    'HTTPBasicAuth', 'HTTPTokenAuth', 'APIKeyHeaderAuth', 'APIKeyCookieAuth', 'APIKeyQueryAuth'
]
TagsType = t.Union[list[str], list[dict[str, t.Any]]]
ViewClassType = type['View']
ViewFuncOrClassType = t.Union[t.Callable, ViewClassType]

ResponseObjectType = dict[str, t.Union[str, dict[str, dict[str, t.Any]]]]
ResponsesObjectType = dict[t.Union[int, str], ResponseObjectType]
ResponsesType = t.Union[list[int], dict[int, str], ResponsesObjectType]

RouteCallableType = t.Union[
    t.Callable[..., ResponseReturnValueType],
    t.Callable[..., t.Awaitable[ResponseReturnValueType]],
]


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
