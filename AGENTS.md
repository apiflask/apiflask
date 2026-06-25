# Repository Guidelines

## Project

APIFlask is a lightweight Python web API framework built on Flask and marshmallow-code projects. It provides a richer set of decorators (`@app.input`, `@app.output`, `@app.doc`, `@app.auth_required`), automatic OpenAPI 3 spec generation, and bundled API documentation UIs (Swagger UI, ReDoc, Elements, RapiDoc).

## Repository Layout

The repo is split into four areas, each with its own guidance file for module-specific context:

- `src/apiflask/` — framework source: classes, decorators, and OpenAPI generation
- `tests/` — pytest suite: fixtures, organization, conventions
- `examples/` — runnable example apps demonstrating individual patterns
- `docs/` — MkDocs documentation site (multi-language)

Key top-level files: `pyproject.toml`, `tox.ini` (env definitions), `mkdocs.yml`, `CHANGES.md`, `CONTRIBUTING.md`, `requirements/` (pinned dep groups: `dev.txt`, `tests.txt`, `docs.txt`, `typing.txt`, `examples.txt`, `min-versions.txt`).

## Common Commands

Run from the repo root unless otherwise noted.

### Setup

```bash
pip install -r requirements/dev.txt
pip install -e .
pre-commit install
```

### Tests

```bash
pytest                                    # all tests
pytest tests/test_app.py                  # single file
pytest tests/test_app.py::test_name       # single test
pytest -k "openapi and not security"      # by expression
tox                                       # full matrix (py3.9-3.14, pypy, style, typing, docs)
tox -e py312                              # one Python version
tox -e minimal                            # smoke import with minimal deps
tox -e min-versions                       # tests against minimum supported deps
```

### Lint & types

```bash
tox -e style           # pre-commit run --all-files
tox -e typing          # mypy
pre-commit run --all-files   # equivalent to tox -e style
```

### Documentation

```bash
mkdocs serve           # live-reload preview at http://127.0.0.1:8000
mkdocs build           # static build -> site/
tox -e docs            # equivalent to mkdocs build
```

## Coding Style & Naming Conventions

- **Formatter/Linter**: Ruff (line length 100, single quotes for inline, double for docstrings).
- **Pre-commit hooks**: `ruff`, `ruff-format`, `pyupgrade`, `reorder-python-imports`, trailing whitespace, end-of-file fixer.
- **Indentation**: 4 spaces.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes. Module-level "private" names prefixed with `_`.
- **Imports**: reordered automatically; place `apiflask` imports under `src/`.
- **Type annotations**: enforced via mypy (strict settings in `pyproject.toml`).

## Testing Guidelines

- **Framework**: pytest. Test files follow `tests/test_*.py`.
- **Coverage**: branch coverage enabled via `--cov=apiflask --cov-branch`; `src/apiflask/_decorators.py` and `views.py` are excluded.
- **Naming**: `test_<descriptive_name>` matching the module or behavior being tested.
- **Shared fixtures**: defined in `tests/conftest.py` and `tests/schemas.py`.
- Each new feature, decorator, or setting gets its own `test_*.py`. Match existing naming patterns (`test_decorator_*`, `test_openapi_*`, `test_settings_*`).
- For tests that need a full app on disk, add it under `tests/test_apps/` and use the `test_apps` fixture.
- Run `pytest` before submitting; run `tox` for the full cross-version matrix.

## Commit & Pull Request Guidelines

- **Commit messages**: use conventional-style prefixes — `feat(scope):`, `fix(scope):`, `docs(scope):`, `perf(scope):`, etc. Scope is typically a module name (e.g., `exceptions`, `openapi`).
- **Pull requests**: link the related issue (`fixes #123`), include tests for code changes, update `CHANGES.md` with an entry, and update docstrings with `Version Added`/`Version Changed` notes where relevant.
- Docs content should wrap at 72 characters per line.

## Dependencies and Their Roles

| Library | Role |
|---|---|
| Flask | WSGI core, routing, request/response |
| apispec + MarshmallowPlugin | Convert marshmallow schemas to OpenAPI JSON Schema; manage `components` |
| marshmallow | Schema base; `Schema`, `fields`, `validators` |
| webargs | Parse and validate request inputs at multiple locations (`json`, `query`, `form`, `headers`, `cookies`, `files`, `path`) |
| flask-marshmallow | URL-aware marshmallow fields recognised by the marshmallow plugin |
| flask-httpauth | Actual HTTP authentication enforcement; APIFlask subclasses it to normalise error responses |
| Pydantic | Alternative schema type; integrated via the in-tree `schema_adapters` registry (not via apispec plugin) |

## Agent-Specific Instructions

- Add or update tests under `tests/` when changing framework source code.
- Public functions/classes need docstrings — they are picked up by `mkdocstrings` and rendered into the docs site under `docs/api/`.
- Public-API additions also need a `__init__.py` re-export and an entry in `CHANGES.md`.
- When adding a new public module under `src/apiflask/`, add a matching stub page under `docs/api/` so `mkdocstrings` can render it.
- Prefer linking to the auto-generated API reference instead of duplicating signatures inside guide pages.
- Keep examples self-contained and minimal — one file or a small package, no shared utilities across examples.
