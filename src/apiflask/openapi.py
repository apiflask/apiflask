from __future__ import annotations

import typing as t

from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .types import HTTPAuthType

if t.TYPE_CHECKING:  # pragma: no cover
    from .blueprint import APIBlueprint


default_bypassed_endpoints: list[str] = [
    'static',
    'openapi.spec',
    'openapi.docs',
    'openapi.redoc',
    'openapi.swagger_ui_oauth_redirect',
    '_debug_toolbar.static',  # Flask-DebugToolbar
]

default_response = {
    'schema': {},
    'status_code': 200,
    'description': None,
    'example': None,
    'examples': None,
    'links': None,
    'content_type': 'application/json',
    'headers': None,
}


def get_tag(blueprint: APIBlueprint, blueprint_name: str) -> dict[str, t.Any]:
    """Get tag from blueprint object."""
    tag: dict[str, t.Any]
    if blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tag = blueprint.tag
        else:
            tag = {'name': blueprint.tag}
    else:
        tag = {'name': blueprint_name.title()}
    return tag


def get_operation_tags(blueprint: APIBlueprint, blueprint_name: str) -> list[str]:
    """Get operation tag from blueprint object."""
    tags: list[str]
    if blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tags = [blueprint.tag['name']]
        else:
            tags = [blueprint.tag]
    else:
        tags = [blueprint_name.title()]
    return tags


def get_auth_name(auth: HTTPAuthType, auth_names: list[str]) -> str:
    """Get auth name from auth object."""
    name: str = ''
    if hasattr(auth, 'security_scheme_name'):
        name = auth.security_scheme_name  # type: ignore
    if not name:
        if isinstance(auth, HTTPBasicAuth):
            name = 'BasicAuth'
        elif isinstance(auth, HTTPTokenAuth):
            if auth.scheme.lower() == 'bearer' and auth.header is None:
                name = 'BearerAuth'
            else:
                name = 'ApiKeyAuth'
        else:
            raise TypeError('Unknown authentication scheme.')

    if name in auth_names:
        v = 2
        new_name = f'{name}_{v}'
        while new_name in auth_names:
            v += 1
            new_name = f'{name}_{v}'
        name = new_name
    return name


def get_security_scheme(auth: HTTPAuthType) -> dict[str, t.Any]:
    """Get security scheme from auth object."""
    security_scheme: dict[str, t.Any]
    if isinstance(auth, HTTPTokenAuth):
        if auth.scheme.lower() == 'bearer' and auth.header is None:
            security_scheme = {
                'type': 'http',
                'scheme': 'bearer',
            }
        else:
            security_scheme = {
                'type': 'apiKey',
                'name': auth.header,
                'in': 'header',
            }
    else:
        security_scheme = {
            'type': 'http',
            'scheme': 'basic',
        }
    return security_scheme


def get_security_and_security_schemes(
    auth_names: list[str], auth_schemes: list[HTTPAuthType]
) -> tuple[dict[HTTPAuthType, str], dict[str, dict[str, str]]]:
    """Make security and security schemes from given auth names and schemes."""
    security: dict[HTTPAuthType, str] = {}
    security_schemes: dict[str, dict[str, str]] = {}
    for name, auth in zip(auth_names, auth_schemes):  # noqa: B905
        security[auth] = name
        security_schemes[name] = get_security_scheme(auth)
        if hasattr(auth, 'description') and auth.description is not None:
            security_schemes[name]['description'] = auth.description
    return security, security_schemes


def get_path_summary(func: t.Callable, fallback: str | None = None) -> str:
    """Get path summary from the name or docstring of the view function."""
    summary: str
    docs: list = (func.__doc__ or '').strip().split('\n')
    if docs[0]:
        # Use the first line of docstring
        summary = docs[0]
    else:
        # Use the function name
        summary = fallback or ' '.join(func.__name__.split('_')).title()
    return summary


def get_path_description(func: t.Callable) -> str:
    """Get path description from the docstring of the view function."""
    docs = (func.__doc__ or '').strip().split('\n')
    if len(docs) > 1:
        # use the remain lines of docstring as description
        return '\n'.join(docs[1:]).strip()
    return ''


def get_argument(argument_type: str, argument_name: str) -> dict[str, t.Any]:
    """Make argument from given type and name."""
    argument: dict[str, t.Any] = {
        'in': 'path',
        'name': argument_name,
    }
    if argument_type == 'int:':
        argument['schema'] = {'type': 'integer'}
    elif argument_type == 'float:':
        argument['schema'] = {'type': 'number'}
    else:
        argument['schema'] = {'type': 'string'}
    return argument
