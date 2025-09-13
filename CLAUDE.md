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

- **schemas.py**: Marshmallow schema definitions and utilities (legacy)
- **schema_adapters/**: New pluggable schema system supporting multiple libraries
  - **base.py**: Abstract base class for schema adapters
  - **marshmallow.py**: Marshmallow integration adapter
  - **pydantic.py**: Pydantic integration adapter
  - **registry.py**: Auto-detection and factory for schema adapters
- **openapi.py**: OpenAPI specification generation
- **openapi_adapters.py**: OpenAPI integration for multiple schema types
- **exceptions.py**: Custom exception classes and error handling
- **security.py**: Authentication utilities (HTTPBasicAuth, HTTPTokenAuth)
- **validators.py**: Re-exports marshmallow validators (legacy)
- **fields.py**: Re-exports marshmallow and Flask-Marshmallow fields (legacy)

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
- marshmallow 3.20+ (serialization/validation) - Optional in v3.0.0+
- flask-marshmallow (Flask integration for marshmallow) - Optional in v3.0.0+
- webargs (request parsing) - Optional in v3.0.0+
- apispec (OpenAPI spec generation)
- flask-httpauth (authentication support)

Optional dependencies:
- pydantic 2.0+ (alternative serialization/validation) - Install with `pip install apiflask[pydantic]`

## Schema Libraries Support

APIFlask 3.0.0+ supports multiple schema libraries:

### Pydantic (Recommended for new projects)
```python
from pydantic import BaseModel
from apiflask import APIFlask

class UserModel(BaseModel):
    id: int
    name: str
    email: str

app = APIFlask(__name__)

@app.post('/users')
@app.input(UserModel)
@app.output(UserModel, status_code=201)
def create_user(json_data: UserModel):
    return UserModel(id=1, name=json_data.name, email=json_data.email)
```

### Marshmallow (Legacy, still supported)
```python
from apiflask import APIFlask, Schema
from apiflask.fields import Integer, String

class UserSchema(Schema):
    id = Integer()
    name = String()
    email = String()

app = APIFlask(__name__)

@app.post('/users')
@app.input(UserSchema)
@app.output(UserSchema, status_code=201)
def create_user(json_data):
    return {'id': 1, 'name': json_data['name'], 'email': json_data['email']}
```

Both approaches work identically with decorators and generate the same OpenAPI documentation.

## Version Support

- Python 3.8+
- Flask 2.0+
- Supports async/await when using Flask 2.0+ with `apiflask[async]`
