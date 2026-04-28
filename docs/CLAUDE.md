# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scope: the APIFlask documentation site. For repo-wide commands see the root `CLAUDE.md`.

## Tooling

- [MkDocs](https://www.mkdocs.org/) with the **Material** theme (`mkdocs-material`).
- [`mkdocstrings`](https://mkdocstrings.github.io/) auto-generates the API reference from Python docstrings under `src/apiflask/`.
- Markdown extensions: admonition, `pymdownx` (highlight, tabbed, superfences, snippets, details), `toc`.

Configuration lives in `mkdocs.yml` at the repo root. Its `watch:` block also watches `src/apiflask`, `README.md`, `CHANGES.md`, and `examples/README.md` so live-reload picks up source/doc changes.

## Local preview

```bash
mkdocs serve     # http://127.0.0.1:8000 with live reload
mkdocs build     # static output → site/
tox -e docs      # equivalent to `mkdocs build`, used in CI
```

## Layout

- Top-level guides: Basic Usage, Request, Response, Schema (marshmallow + Pydantic), Authentication, OpenAPI, API Docs, Configuration, Error Handling, Examples, Tips.
- Migration guides: from Flask, from Flask-RESTPlus / RESTX.
- `docs/api/` — auto-generated API reference. Each page is a thin stub pointing `mkdocstrings` at a module under `src/apiflask/` (APIFlask, APIBlueprint, Exceptions, OpenAPI, Schemas, Schema Adapters, Fields, Validators, Route, Security, Helpers, Commands).
- Meta: `changelog.md` is sourced from the root `CHANGES.md`; `contributing.md` is sourced from `CONTRIBUTING.md`.
- Assets and theme overrides live in `docs/_assets/` and `docs/_templates/`.

## Translations

Three independently deployed sites, declared under `extra.alternate` in `mkdocs.yml`:

- English — `apiflask.com`
- فارسی (Persian) — `fa.apiflask.com`
- 简体中文 (Simplified Chinese) — `zh.apiflask.com`

These are separate deployments, not subdirectories of a single MkDocs build.

## Conventions

- When adding a new public module under `src/apiflask/`, add a matching stub page under `docs/api/` so `mkdocstrings` can render it.
- User-facing changes belong in `CHANGES.md` (which becomes `changelog.md` in the docs).
- Prefer linking to the auto-generated API reference instead of duplicating signatures inside guide pages.
