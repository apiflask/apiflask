from functools import wraps

from flask import Response
from webargs.flaskparser import FlaskParser as BaseFlaskParser

from apifairy.exceptions import ValidationError


class FlaskParser(BaseFlaskParser):
    DEFAULT_VALIDATION_STATUS = 400

    def handle_error(self, error, req, schema, *, error_status_code,
                     error_headers):
        raise ValidationError(
            error_status_code or self.DEFAULT_VALIDATION_STATUS,
            error.messages)


parser = FlaskParser()
use_args = parser.use_args


def _annotate(f, **kwargs):
    if not hasattr(f, '_spec'):
        f._spec = {}
    for key, value in kwargs.items():
        f._spec[key] = value


def authenticate(auth, **kwargs):
    def decorator(f):
        roles = kwargs.get('role')
        if not isinstance(roles, list):  # pragma: no cover
            roles = [roles] if roles is not None else []
        _annotate(f, auth=auth, roles=roles)
        return auth.login_required(**kwargs)(f)
    return decorator


def arguments(schema, location='query', **kwargs):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        if not hasattr(f, '_spec') or f._spec.get('args') is None:
            _annotate(f, args=[])
        f._spec['args'].append((schema, location))
        return use_args(schema, location=location, **kwargs)(f)
    return decorator


def body(schema, **kwargs):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        _annotate(f, body=schema)
        return use_args(schema, location='json', **kwargs)(f)
    return decorator


def response(schema, status_code=200, description=None):
    if isinstance(schema, type):  # pragma: no cover
        schema = schema()

    def decorator(f):
        _annotate(f, response=schema, status_code=status_code,
                  description=description)

        @wraps(f)
        def _response(*args, **kwargs):
            rv = f(*args, **kwargs)
            if isinstance(rv, Response):  # pragma: no cover
                raise RuntimeError(
                    'The @response decorator cannot handle Response objects.')
            if isinstance(rv, tuple):
                json = schema.jsonify(rv[0])
                if len(rv) == 2:
                    if not isinstance(rv[1], int):
                        rv = (json, status_code, rv[1])
                    else:
                        rv = (json, rv[1])
                elif len(rv) >= 3:
                    rv = (json, rv[1], rv[2])
                else:
                    rv = json
                return rv
            else:
                return schema.jsonify(rv), status_code
        return _response
    return decorator


def other_responses(responses):
    def decorator(f):
        _annotate(f, other_responses=responses)
        return f
    return decorator
