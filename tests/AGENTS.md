# Test Suite Guidelines

Scope: the APIFlask test suite. For commands (`pytest`, `tox`, …) see the root [AGENTS.md](../AGENTS.md).

## Framework

[pytest](https://pytest.org). Common fixtures live in `conftest.py`:

- `app` — a bare `APIFlask(__name__)` instance.
- `client` — `app.test_client()`.
- `cli_runner` — `app.test_cli_runner()`.
- `test_apps` — adds `tests/test_apps/` to `sys.path` so the small helper apps in that directory can be imported.

Shared schemas used across tests live in `tests/schemas.py`. Prefer reusing them over defining new ones inline.

## Organisation

Tests are grouped by feature/module, one file per area:

- Decorators: `test_decorator_input.py`, `test_decorator_output.py`, `test_decorator_doc.py`, `test_decorator_auth_required.py`, `test_decorators.py`.
- OpenAPI spec: `test_openapi_basic.py`, `test_openapi_parameters.py`, `test_openapi_security.py`, `test_openapi_tags.py`, etc.
- Settings: `test_settings_api_docs.py`, `test_settings_auto_behaviour.py`, `test_settings_openapi_spec.py`, etc.
- Integrations: `test_pydantic_integration.py`, `test_decoupling_integration.py`, `test_async.py`.
- Core: `test_app.py`, `test_blueprint.py`, `test_exceptions.py`, `test_fields.py`, `test_schemas.py`, `test_route.py`, …

## Conventions

- Each new feature, decorator, or setting gets its own `test_*.py`. Match the existing naming pattern (`test_decorator_*`, `test_openapi_*`, `test_settings_*`).
- Reuse fixtures from `conftest.py` rather than building fresh `APIFlask` instances when possible.
- Reuse schemas from `tests/schemas.py`; only inline a schema when the test specifically needs a shape that isn't shared.
- For tests that need a full app on disk, add it under `tests/test_apps/` and use the `test_apps` fixture.
- Keep tests deterministic — no network calls, no time-dependent assertions.
