# AGENTS.md

APIFlask is a lightweight Python web API framework based on Flask, supporting both marshmallow
schemas and Pydantic models through a pluggable schema adapter system.


## General Rules and Guidelines

Follow the contribution workflow in CONTRIBUTING.md strictly. The most important rules:

- If there is not an open issue for what you want to submit, prefer opening one for discussion
  before working on a PR.
- Keep AI-assisted PRs tightly isolated to the requested change and never include unrelated cleanup
  or opportunistic improvements unless they are strictly necessary for correctness.
- Include tests if your patch adds or changes code. Make sure the test fails without your patch.
- Update any relevant docs pages and docstrings. Docs pages and docstrings should be wrapped at
  72 characters.
- Add an entry in `CHANGES.md`. Use the same style as other entries. Also include
  `Version Changed` or `Version Added` section in relevant docstrings.


## Structure

- `src/apiflask/` - Main source code
  - `app.py` - Core `APIFlask` application class (extends Flask)
  - `scaffold.py` - Route decorators (`@app.input()`, `@app.output()`, `@app.get()`, etc.)
  - `security.py` - Authentication classes (HTTPBasicAuth, HTTPTokenAuth, APIKey*, MultiAuth)
  - `schemas.py` - Base schema classes and built-in schemas (Schema, FileSchema, Pagination)
  - `openapi.py` / `openapi_adapters.py` - OpenAPI spec generation and schema adapter system
  - `exceptions.py` - HTTPError and abort helper
  - `settings.py` - Configuration attributes
  - `validators.py` / `fields.py` - Re-exported marshmallow validators and fields
  - `commands.py` - CLI command (`flask spec`)
  - `types.py` - Type definitions
- `tests/` - Test suite (pytest)
- `examples/` - Example applications (also run as part of test suite)
- `docs/` - MkDocs documentation source
- `requirements/` - Pinned dependency files (pip-compile-multi managed)


## Commands

```bash
# First time setup
python3 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements/dev.txt
pip install -e .
pre-commit install

# Run tests
pytest

# Run a single test file
pytest tests/test_app.py

# Run a single test function
pytest tests/test_app.py::test_function_name -v

# Run full CI suite (tests + style + typing + docs)
tox

# Run only style checks
tox -e style

# Run only type checking
tox -e typing

# Run pre-commit hooks manually
pre-commit run --all-files

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```


## Coding Conventions

- Use **single quotes** for strings (configured in ruff).
- Line length limit is **100 characters**.
- Import ordering is handled by `reorder-python-imports` (application directory is `src`).
- The `examples/` directory is excluded from import reordering.
- ruff is the linter and formatter (replaces flake8/black). Run via pre-commit.
- Type annotations are checked with mypy (`tool.mypy` in pyproject.toml). Do not add
  `type: ignore` comments—solve type errors properly or note them for a follow-up.
- Python target version: 3.9+ (use `pyupgrade --py38-plus` via pre-commit).
- Tests use pytest with coverage (`--cov=apiflask --cov-branch`). Test paths include both
  `tests/` and `examples/`.


## Commit Formatting

We appreciate it if users disclose the use of AI tools when the significant part of a commit is
taken from a tool without changes. When making a commit this should be disclosed through an
`Assisted-by:` commit message trailer.

Examples:

```
Assisted-by: Qoder
Assisted-by: ChatGPT 5.2
Assisted-by: Claude Opus 4.6
```
