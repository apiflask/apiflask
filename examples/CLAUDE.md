# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scope: the APIFlask example apps. For repo-wide commands see the root `CLAUDE.md`.

## Purpose

Each subdirectory under `examples/` is a self-contained Flask app demonstrating one APIFlask pattern. Examples are deliberately minimal — they exist to be read and copied, not to be production-ready.

## Catalog

| Directory | Demonstrates |
|---|---|
| `basic` | Minimal APIFlask app |
| `auth` | `HTTPBasicAuth`, `HTTPTokenAuth` |
| `blueprint_tags` | `APIBlueprint` + OpenAPI tags |
| `cbv` | Class-based views via `MethodView` |
| `dataclass` | Python dataclasses as schemas |
| `file_upload` | File upload handling |
| `openapi` | Customising the generated OpenAPI spec |
| `orm` | SQLAlchemy ORM integration |
| `otel` | OpenTelemetry tracing integration |
| `pagination` | Pagination pattern with `pagination_builder` |
| `pydantic` | Pydantic models as schemas |
| `base_response` | Custom base response class |

## Running an example

```bash
cd examples/<name>
pip install -r ../requirements.txt   # or requirements/examples.txt at repo root
flask run
```

Open the docs UI at `http://127.0.0.1:5000/docs` (Swagger UI) or `/redoc`.

## Conventions

- Keep each example **self-contained** and **minimal** — one file or a small package, no shared utilities across examples.
- A new example must:
  - Have a short description in `examples/README.md`.
  - Usually be referenced from a section of `docs/` (see `docs/CLAUDE.md`).
  - Run cleanly under `flask run` with only the dependencies listed in `requirements/examples.txt`.
