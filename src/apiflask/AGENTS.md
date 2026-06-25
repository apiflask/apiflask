# APIFlask Framework Source Guidelines

Scope: the APIFlask framework source. For repo-wide commands see the root [AGENTS.md](../AGENTS.md).

## Class hierarchy

```
APIFlask(APIScaffold, Flask)            # app.py
APIBlueprint(APIScaffold, Blueprint)    # blueprint.py
APIScaffold                             # scaffold.py — owns ALL decorators
```

`APIScaffold` is a mixin holding the API-shaping decorators (`input`, `output`, `doc`, `auth_required`) plus HTTP method shortcuts (`get`, `post`, …). Both `APIFlask` and `APIBlueprint` get those decorators by inheriting it.

## Module map

- `app.py` — `APIFlask` class. Owns spec generation (`_generate_spec`, lazy `app.spec`), spec/docs routes, error handling setup, `@spec_processor`.
- `blueprint.py` — `APIBlueprint`: `Blueprint` + `APIScaffold` plus `tag` / `enable_openapi` attributes.
- `scaffold.py` — the decorator implementations.
- `route.py` — patches Flask's `route()` so `MethodView` `_method_spec` dicts are picked up.
- `openapi.py` — pure helpers used during spec assembly (tags, summaries, parameter building, security-scheme resolution).
- `security.py` — `HTTPBasicAuth`, `HTTPTokenAuth`, header/cookie/query API-key auth, `MultiAuth`. Thin wrappers over flask-httpauth that add `get_security_scheme()` and APIFlask error responses.
- `schemas.py` — `Schema` (alias for marshmallow `Schema`), `EmptySchema`, `FileSchema`, `PaginationSchema`, `PaginationModel` (Pydantic), plus raw OpenAPI dicts for validation/HTTP error schemas.
- `fields.py`, `validators.py` — pass-throughs over marshmallow + flask-marshmallow.
- `exceptions.py` — `HTTPError`, `abort()`.
- `commands.py` — Flask CLI commands, e.g. `flask spec`.
- `helpers.py` — `pagination_builder`, `get_reason_phrase`, sentinels.
- `settings.py` — every supported `app.config` key declared as a class attribute (for IDE / type help).
- `types.py` — shared `TypeAlias` definitions.
- `views.py` — re-export of Flask's `MethodView`.
- `ui_templates.py` — HTML for Swagger UI / ReDoc / Elements / RapiDoc.
- `schema_adapters/` — registry that lets non-marshmallow schemas (Pydantic, dataclasses) plug into `@input`/`@output`.
- `openapi_adapters/` — adapters that turn non-marshmallow schemas into OpenAPI fragments during spec generation.

## Decorator pattern

All decorators follow the same shape:

1. Call `_annotate(f, key=value)` to merge metadata into `f._spec` — pure metadata, no HTTP behaviour.
2. Optionally wrap `f` with runtime behaviour:
   - `@input` → `parser.use_args()` (webargs / marshmallow) or a Pydantic adapter; injects validated data as a kwarg.
   - `@output` → `_response()` which calls the schema adapter's `serialize_output()` and `jsonify()`.
   - `@auth_required` → flask-httpauth's `login_required()`.
   - `@doc` → metadata only, no wrapping.

This means decorator order largely doesn't matter and there is zero spec-generation overhead on normal requests.

## OpenAPI spec generation

Lazy. First access to `app.spec` (or `GET /openapi.json`) triggers `_generate_spec()`:

1. Build an `apispec.APISpec` with `MarshmallowPlugin` + any user-registered `spec_plugins`.
2. Walk `url_map.iter_rules()`. For each view function read its `_spec` dict (set by decorators) — and for `MethodView`s, the per-method `_method_spec` dicts captured by `route.py`.
3. Assemble `paths` / `operations`: input schemas → `requestBody`, output schemas → `responses`, query/header/path/cookie args → `parameters`. Schema resolution goes through apispec's `MarshmallowPlugin` for marshmallow, or `openapi_adapters` for Pydantic / dataclasses.
4. Collect security schemes by scanning view functions for `_spec['auth']`.
5. If a `@app.spec_processor` is registered, run it on the final dict.
6. Cache to `self._spec`.

## Public API (`__init__.py`)

`APIFlask`, `APIBlueprint`, `HTTPError`, `abort`, `Schema`, `EmptySchema`, `FileSchema`, `PaginationSchema`, `PaginationModel`, `HTTPBasicAuth`, `HTTPTokenAuth`, `APIKeyHeaderAuth`, `APIKeyCookieAuth`, `APIKeyQueryAuth`, `MultiAuth`, `get_reason_phrase`, `pagination_builder`, plus `fields` and `validators` modules.

## When editing here

- Add or update tests under `tests/` (file-per-feature, see [tests AGENTS.md](../../tests/AGENTS.md)).
- Public functions/classes need docstrings — they are picked up by `mkdocstrings` and rendered into the docs site under `docs/api/`. When adding a new public module, add a matching stub under `docs/api/` (see [docs AGENTS.md](../../docs/AGENTS.md)).
- Public-API additions also need a `__init__.py` re-export and an entry in `CHANGES.md`.
