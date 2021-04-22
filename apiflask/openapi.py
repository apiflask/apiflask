import sys
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from apispec import APISpec

from .blueprint import APIBlueprint
from .security import HTTPBasicAuth
from .security import HTTPTokenAuth
from .types import HTTPAuthType
from .types import SchemaType


def get_tag_from_blueprint(
    blueprint: APIBlueprint,
    blueprint_name: str
) -> Dict[str, Any]:
    tag: Dict[str, Any]
    if hasattr(blueprint, 'tag') and blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tag = blueprint.tag
        else:
            tag = {'name': blueprint.tag}
    else:
        tag = {'name': blueprint_name.title()}
        module = sys.modules[blueprint.import_name]
        if module.__doc__:
            tag['description'] = module.__doc__.strip()
    return tag


def get_operation_tags_from_blueprint(
    blueprint: APIBlueprint,
    blueprint_name: str
) -> List[str]:
    tags: List[str]
    if hasattr(blueprint, 'tag') and blueprint.tag is not None:
        if isinstance(blueprint.tag, dict):
            tags = [blueprint.tag['name']]
        else:
            tags = [blueprint.tag]
    else:
        tags = [blueprint_name.title()]
    return tags


def get_auth_name_from_auth_object(
    auth: HTTPAuthType,
    auth_names: List[str]
) -> str:
    name: str
    if isinstance(auth, HTTPBasicAuth):
        name = 'BasicAuth'
    elif isinstance(auth, HTTPTokenAuth):
        if auth.scheme == 'Bearer' and auth.header is None:
            name = 'BearerAuth'
        else:
            name = 'ApiKeyAuth'
    else:
        raise RuntimeError('Unknown authentication scheme')
    if name in auth_names:
        v = 2
        new_name = f'{name}_{v}'
        while new_name in auth_names:
            v += 1
            new_name = f'{name}_{v}'
        name = new_name
    return name


def get_security_scheme_from_auth_object(auth: HTTPAuthType) -> Dict[str, Any]:
    security_scheme: Dict[str, Any]
    if isinstance(auth, HTTPTokenAuth):
        if auth.scheme == 'Bearer' and auth.header is None:
            security_scheme = {
                'type': 'http',
                'scheme': 'Bearer',
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
            'scheme': 'Basic',
        }
    return security_scheme


def make_security_and_security_schemes(
    auth_names: List[str],
    auth_schemes: List[HTTPAuthType]
) -> Tuple[Dict[HTTPAuthType, str], Dict[str, Dict[str, str]]]:
    security: Dict[HTTPAuthType, str] = {}
    security_schemes: Dict[str, Dict[str, str]] = {}
    for name, auth in zip(auth_names, auth_schemes):
        security[auth] = name
        security_schemes[name] = get_security_scheme_from_auth_object(auth)
        if hasattr(auth, 'description') and auth.description is not None:
            security_schemes[name]['description'] = auth.description
    return security, security_schemes


def get_summary_from_view_func(func: Callable) -> str:
    summary: str
    docs: list = (func.__doc__ or '').strip().split('\n')
    if docs[0]:
        # Use the first line of docstring as summary
        summary = docs[0]
    else:
        # Use the function name as summary
        summary = ' '.join(func.__name__.split('_')).title()
    return summary


def add_response_to_operation(
    operation: dict,
    status_code: str,
    schema: SchemaType,
    description: str,
    example: Optional[Any] = None,
    examples: Optional[Dict[str, Any]] = None,
) -> None:
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


def add_response_with_schema_to_operation(
    spec: APISpec,
    operation: dict,
    status_code: str,
    schema: SchemaType,
    schema_name: str,
    description: str
) -> None:
    if isinstance(schema, type):
        schema = schema()  # type: ignore
        add_response_to_operation(operation, status_code, schema, description)
    elif isinstance(schema, dict):
        if schema_name not in spec.components.schemas:
            spec.components.schema(schema_name, schema)
        schema_ref = {'$ref': f'#/components/schemas/{schema_name}'}
        add_response_to_operation(operation, status_code, schema_ref, description)
    else:
        raise RuntimeError(
            'The schema must be a Marshamallow schema \
            class or an OpenAPI schema dict.'
        )


def make_argument(argument_type: str, argument_name: str) -> Dict[str, Any]:
    argument: Dict[str, Any] = {
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
