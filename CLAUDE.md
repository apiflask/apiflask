# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

APIFlask is a lightweight Python web API framework built on Flask and marshmallow-code projects. It provides a richer set of decorators (`@app.input`, `@app.output`, `@app.doc`, `@app.auth_required`), automatic OpenAPI 3 spec generation, and bundled API documentation UIs (Swagger UI, ReDoc, Elements, RapiDoc).

## Repository Layout

The repo is split into four areas, each with its own `CLAUDE.md` for module-specific guidance:

- `src/apiflask/CLAUDE.md` — framework source: classes, decorators, and OpenAPI generation
- `tests/CLAUDE.md` — pytest suite: fixtures, organization, conventions
- `examples/CLAUDE.md` — runnable example apps demonstrating individual patterns
- `docs/CLAUDE.md` — MkDocs documentation site (multi-language)

Other top-level files: `pyproject.toml`, `tox.ini` (env definitions), `mkdocs.yml`, `CHANGES.md`, `CONTRIBUTING.md`, `requirements/` (pinned dep groups: `dev.txt`, `tests.txt`, `docs.txt`, `typing.txt`, `examples.txt`, `min-versions.txt`).

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
tox                                       # full matrix (py3.9–3.14, pypy, style, typing, docs)
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
mkdocs build           # static build → site/
tox -e docs            # equivalent to mkdocs build
```

## Dependencies and their roles

| Library | Role |
|---|---|
| Flask | WSGI core, routing, request/response |
| apispec + MarshmallowPlugin | Convert marshmallow schemas → OpenAPI JSON Schema; manage `components` |
| marshmallow | Schema base; `Schema`, `fields`, `validators` |
| webargs | Parse and validate request inputs at multiple locations (`json`, `query`, `form`, `headers`, `cookies`, `files`, `path`) |
| flask-marshmallow | URL-aware marshmallow fields recognised by the marshmallow plugin |
| flask-httpauth | Actual HTTP authentication enforcement; APIFlask subclasses it to normalise error responses |
| Pydantic | Alternative schema type; integrated via the in-tree `schema_adapters` registry (not via apispec's plugin) |
