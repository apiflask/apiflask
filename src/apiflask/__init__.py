import typing as t

from . import fields as fields
from . import validators as validators
from .app import APIFlask as APIFlask
from .blueprint import APIBlueprint as APIBlueprint
from .exceptions import abort as abort
from .exceptions import HTTPError as HTTPError
from .helpers import get_reason_phrase as get_reason_phrase
from .helpers import pagination_builder as pagination_builder
from .schemas import EmptySchema as EmptySchema
from .schemas import FileSchema as FileSchema
from .schemas import PaginationSchema as PaginationSchema
from .schemas import Schema as Schema
from .security import HTTPBasicAuth as HTTPBasicAuth
from .security import HTTPTokenAuth as HTTPTokenAuth


def __getattr__(name: str) -> t.Any:  # pragma: no cover
    if name == '__version__':
        import importlib.metadata
        import warnings

        warnings.warn(
            "The '__version__' attribute is deprecated and will be removed in"
            ' APIFlask 3.0.0. Use feature detection or'
            ' \'importlib.metadata.version("apiflask")\' instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return importlib.metadata.version('apiflask')

    raise AttributeError(name)
