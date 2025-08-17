# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

APIFlask is a lightweight Python web API framework based on Flask and marshmallow. It provides automatic request validation, response serialization, and OpenAPI documentation generation.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install development dependencies
pip install -r requirements/dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run basic tests
pytest

# Run tests with coverage
pytest --cov=apiflask --cov-branch --cov-report=term-missing

# Run full test suite with tox (includes style, typing, docs)
tox

# Run specific test environments
tox -e style      # Code style checks
tox -e typing     # Type checking with mypy
tox -e docs       # Documentation build
tox -e minimal    # Test with minimal dependencies
```

### Code Quality
```bash
# Run pre-commit checks on all files
pre-commit run --all-files

# Type checking
mypy

# Format code (configured in pyproject.toml)
ruff format

# Lint code
ruff check
```

### Documentation
```bash
# Serve live documentation with auto-reload
mkdocs serve

# Build documentation
mkdocs build

# View built docs at site/index.html
```

### Example Testing
```bash
# Run example application tests
pytest examples/
```

## Architecture

### Core Components

**APIFlask (src/apiflask/app.py)**: Main application class extending Flask with API-specific functionality including OpenAPI spec generation, automatic error handling, and decorators for input/output validation.

**APIBlueprint (src/apiflask/blueprint.py)**: Blueprint class extending Flask's Blueprint with API features for organizing related endpoints.

**APIScaffold (src/apiflask/scaffold.py)**: Base class providing common functionality for both APIFlask and APIBlueprint, including the core decorators (`@input`, `@output`, `@doc`, etc.).

**Decorators**: The framework's main value comes from decorators that handle:
- `@app.input()` - Request validation and deserialization
- `@app.output()` - Response serialization and documentation
- `@app.doc()` - OpenAPI documentation metadata
- `@app.auth_required()` - Authentication requirements

### Key Modules

- **schemas.py**: Marshmallow schema definitions and utilities
- **openapi.py**: OpenAPI specification generation
- **exceptions.py**: Custom exception classes and error handling
- **security.py**: Authentication utilities (HTTPBasicAuth, HTTPTokenAuth)
- **validators.py**: Re-exports marshmallow validators
- **fields.py**: Re-exports marshmallow and Flask-Marshmallow fields

### Project Structure

- `src/apiflask/`: Main source code
- `tests/`: Test suite with comprehensive coverage
- `examples/`: Working examples demonstrating features
- `docs/`: MkDocs documentation source
- `requirements/`: Pinned dependencies for different environments

## Testing Strategy

Tests are organized by module and feature:
- Unit tests for individual components
- Integration tests for decorator combinations
- OpenAPI spec generation tests
- Example application tests to ensure examples stay working

Test apps in `tests/test_apps/` provide fixtures for testing framework functionality.

## Dependencies

Core dependencies:
- Flask 2.0+ (base framework)
- marshmallow 3.20+ (serialization/validation)
- flask-marshmallow (Flask integration for marshmallow)
- webargs (request parsing)
- apispec (OpenAPI spec generation)
- flask-httpauth (authentication support)

## Version Support

- Python 3.8+
- Flask 2.0+
- Supports async/await when using Flask 2.0+ with `apiflask[async]`
