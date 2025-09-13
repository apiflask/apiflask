# APIFlask Pydantic Example

This example demonstrates how to use Pydantic models with APIFlask for request validation and response serialization.

## Features Demonstrated

- **Input validation** with Pydantic models for JSON, query parameters, and form data
- **Output serialization** with Pydantic models
- **Automatic OpenAPI documentation** generation from Pydantic models
- **Type hints** and validation with Pydantic
- **Mixed usage** - you can use both Pydantic and marshmallow schemas in the same application

## Installation

First, install APIFlask with Pydantic support:

```bash
pip install apiflask[pydantic]
```

Or install the dependencies separately:

```bash
pip install apiflask pydantic[email]
```

## Running the Example

```bash
python app.py
```

Then visit:
- API documentation: http://localhost:5000/docs
- Hello endpoint: http://localhost:5000/
- Get all pets: http://localhost:5000/pets
- Get specific pet: http://localhost:5000/pets/1

## Key Differences from Marshmallow

### Model Definition

**Pydantic:**
```python
from pydantic import BaseModel

class Pet(BaseModel):
    id: int
    name: str
    category: str
```

**Marshmallow:**
```python
from apiflask import Schema
from apiflask.fields import Integer, String

class Pet(Schema):
    id = Integer()
    name = String()
    category = String()
```

### Usage in Decorators

The decorator usage is identical:

```python
@app.input(PetModel, location='json')
@app.output(PetModel)
def create_pet(json_data):
    # json_data is a Pydantic model instance
    return PetModel(id=1, name=json_data.name, category=json_data.category)
```

### Validation

Pydantic provides:
- Type validation based on Python type hints
- Built-in validators for common types (email, URL, etc.)
- Custom validators
- Automatic conversion when possible

### OpenAPI Documentation

Both Pydantic and marshmallow models automatically generate OpenAPI schemas. Pydantic uses its built-in JSON schema generation.

## API Endpoints

- `GET /` - Hello message
- `GET /pets` - List all pets (with optional query parameters)
- `GET /pets/<id>` - Get specific pet
- `POST /pets` - Create new pet (JSON)
- `PATCH /pets/<id>` - Update pet
- `DELETE /pets/<id>` - Delete pet
- `POST /pets/form` - Create pet from form data

## Testing the API

### Create a new pet:
```bash
curl -X POST http://localhost:5000/pets \
     -H "Content-Type: application/json" \
     -d '{"name": "Buddy", "category": "dog"}'
```

### Get pets with filtering:
```bash
curl "http://localhost:5000/pets?category=dog&limit=5"
```

### Create pet with form data:
```bash
curl -X POST http://localhost:5000/pets/form \
     -d "name=Fluffy&category=cat"
```
