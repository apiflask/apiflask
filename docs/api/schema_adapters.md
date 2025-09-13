# Schema Adapters

The schema adapter system provides a pluggable architecture for supporting different schema libraries in APIFlask.

## Base Classes

::: apiflask.schema_adapters.base

## Registry

::: apiflask.schema_adapters.registry

## Adapters

### Marshmallow Adapter

::: apiflask.schema_adapters.marshmallow

### Pydantic Adapter

::: apiflask.schema_adapters.pydantic

## Usage

The schema adapter system works automatically - you don't need to interact with these classes directly. Simply use marshmallow schemas or Pydantic models with the `@app.input` and `@app.output` decorators, and APIFlask will automatically detect the schema type and use the appropriate adapter.

### Example with automatic detection:

```python
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer
from pydantic import BaseModel, Field

app = APIFlask(__name__)

# Marshmallow schema - automatically detected
class PetIn(Schema):
    name = String(required=True)
    age = Integer()

# Pydantic model - automatically detected
class PetOut(BaseModel):
    id: int = Field(..., description="Pet ID")
    name: str
    age: int

@app.post('/pets')
@app.input(PetIn)       # Uses MarshmallowAdapter
@app.output(PetOut)     # Uses PydanticAdapter
def create_pet(json_data):
    return {'id': 1, 'name': json_data['name'], 'age': json_data['age']}
```

The registry automatically creates the appropriate adapter based on the schema type, handles validation, serialization, and OpenAPI spec generation.

## Extension

The adapter system is designed to be extensible. You can create custom adapters by inheriting from `SchemaAdapter` and registering them with the registry. See the base classes documentation for details on the required interface.
