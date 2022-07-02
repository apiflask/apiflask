import sys
import typing as t

if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # pragma: no cover
    from typing_extensions import Protocol

if t.TYPE_CHECKING:  # pragma: no cover
    from flask.wrappers import Response  # noqa: F401
    from flask.views import View  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401
    from _typeshed.wsgi import WSGIApplication  # noqa: F401
    from .fields import Field  # noqa: F401
    from .schemas import Schema  # noqa: F401
    from .security import HTTPBasicAuth  # noqa: F401
    from .security import HTTPTokenAuth  # noqa: F401
    from .exceptions import HTTPError  # noqa: F401


DecoratedType = t.TypeVar('DecoratedType', bound=t.Callable[..., t.Any])
RequestType = t.TypeVar('RequestType')

ResponseBodyType = t.Union[
    str, bytes, list, t.Dict[str, t.Any], t.Generator[str, None, None], 'Response'
]
ResponseStatusType = t.Union[str, int]
_HeaderName = str
_HeaderValue = t.Union[str, t.List[str], t.Tuple[str, ...]]
ResponseHeaderType = t.Union[
    t.Dict[_HeaderName, _HeaderValue],
    t.Mapping[_HeaderName, _HeaderValue],
    t.List[t.Tuple[_HeaderName, _HeaderValue]],
    'Headers'
]
ResponseReturnValueType = t.Union[
    ResponseBodyType,
    t.Tuple[ResponseBodyType, ResponseStatusType],
    t.Tuple[ResponseBodyType, ResponseHeaderType],
    t.Tuple[ResponseBodyType, ResponseStatusType, ResponseHeaderType],
    'WSGIApplication'
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
