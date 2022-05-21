from __future__ import annotations

import typing as t

from apispec import APISpec

from .exceptions import _bad_schema_message
from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .types import HTTPAuthType
from .types import OpenAPISchemaType
from .types import SchemaType

if t.TYPE_CHECKING:  # pragma: no cover
    from .blueprint import APIBlueprint


default_response = {
    'schema': {},
    'status_code': 200,
    'description': None,
    'example': None,
    'examples': None,
    'links': None,
}


def get_tag(
    blueprint: APIBlueprint,
    blueprint_name: str
) -> t.Dict[str, t.Any]:
    """Get tag from blueprint object."""
    tag: t.Dict[str, t.Any]
    if blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tag = blueprint.tag
        else:
            tag = {'name': blueprint.tag}
    else:
        tag = {'name': blueprint_name.title()}
    return tag


def get_operation_tags(
    blueprint: APIBlueprint,
    blueprint_name: str
) -> t.List[str]:
    """Get operation tag from blueprint object."""
    tags: t.List[str]
    if blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tags = [blueprint.tag['name']]
        else:
            tags = [blueprint.tag]
    else:
        tags = [blueprint_name.title()]
    return tags


def get_auth_name(
    auth: HTTPAuthType,
    auth_names: t.List[str]
) -> str:
    """Get auth name from auth object."""
    name: str
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


def get_security_scheme(auth: HTTPAuthType) -> t.Dict[str, t.Any]:
    """Get security scheme from auth object."""
    security_scheme: t.Dict[str, t.Any]
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
    auth_names: t.List[str],
    auth_schemes: t.List[HTTPAuthType]
) -> t.Tuple[t.Dict[HTTPAuthType, str], t.Dict[str, t.Dict[str, str]]]:
    """Make security and security schemes from given auth names and schemes."""
    security: t.Dict[HTTPAuthType, str] = {}
    security_schemes: t.Dict[str, t.Dict[str, str]] = {}
    for name, auth in zip(auth_names, auth_schemes):
        security[auth] = name
        security_schemes[name] = get_security_scheme(auth)
        if hasattr(auth, 'description') and auth.description is not None:
            security_schemes[name]['description'] = auth.description
    return security, security_schemes


def get_path_summary(func: t.Callable, fallback: t.Optional[str] = None) -> str:
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


def add_response(
    operation: dict,
    status_code: str,
    schema: t.Union[SchemaType, dict],
    description: str,
    example: t.Optional[t.Any] = None,
    examples: t.Optional[t.Dict[str, t.Any]] = None,
    links: t.Optional[t.Dict[str, t.Any]] = None,
) -> None:
    """Add response to operation.

    *Version changed: 0.10.0*

    - Add `links` parameter.
    """
    operation['responses'][status_code] = {}
    if status_code != '204':
        operation['responses'][status_code]['content'] = {
            'application/json': {
                'schema': schema
            }
        }
    operation['responses'][status_code]['description'] = description
    if example is not None:
        operation['responses'][status_code]['content'][
            'application/json']['example'] = example
    if examples is not None:
        operation['responses'][status_code]['content'][
            'application/json']['examples'] = examples
    if links is not None:
        operation['responses'][status_code]['links'] = links


def add_response_with_schema(
    spec: APISpec,
    operation: dict,
    status_code: str,
    schema: OpenAPISchemaType,
    schema_name: str,
    description: str
) -> None:
    """Add response with given schema to operation."""
    if isinstance(schema, type):
        schema = schema()
        add_response(operation, status_code, schema, description)
    elif isinstance(schema, dict):
        if schema_name not in spec.components.schemas:
            spec.components.schema(schema_name, schema)
        schema_ref = {'$ref': f'#/components/schemas/{schema_name}'}
        add_response(operation, status_code, schema_ref, description)
    else:
        raise TypeError(_bad_schema_message)


def get_argument(argument_type: str, argument_name: str) -> t.Dict[str, t.Any]:
    """Make argument from given type and name."""
    argument: t.Dict[str, t.Any] = {
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
