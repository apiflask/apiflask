# Migration Guide

## Migrate to APIFlask 3.x

### New Schema Adapter System

APIFlask 3.x introduces a new pluggable schema adapter system that supports both marshmallow schemas and Pydantic models. This change is **fully backward compatible** - all existing marshmallow-based applications will continue to work without any code changes.

#### What's New

- **Pydantic Support**: You can now use Pydantic models alongside marshmallow schemas
- **Mixed Usage**: Use both marshmallow and Pydantic schemas in the same application
- **Automatic Detection**: APIFlask automatically detects the schema type and uses the appropriate adapter
- **Full Compatibility**: All existing marshmallow functionality remains unchanged

#### No Migration Required for Existing Apps

If you're using marshmallow schemas, **no changes are needed**. Your existing code will continue to work exactly as before:

```python
# This continues to work unchanged
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer

class PetIn(Schema):
    name = String(required=True)
    age = Integer()

@app.input(PetIn)
def create_pet(json_data):
    return {'message': 'created'}
```

#### New: Using Pydantic Models

You can now optionally use Pydantic models for modern, type-hint based validation:

```python
from pydantic import BaseModel, Field

class PetIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=30)

@app.input(PetIn)  # Works with the same decorators
def create_pet(json_data):
    return {'message': 'created'}
```

#### Mixed Usage Example

You can mix both approaches in the same application:

```python
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer
from pydantic import BaseModel, Field

# Marshmallow for input
class UserIn(Schema):
    username = String(required=True)
    email = String(required=True)

# Pydantic for output
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

@app.post('/users')
@app.input(UserIn)      # Marshmallow
@app.output(UserOut)    # Pydantic
def create_user(json_data):
    return {
        'id': 1,
        'username': json_data['username'],
        'email': json_data['email'],
        'created_at': '2023-01-01T00:00:00Z'
    }
```

#### Installation for Pydantic

To use Pydantic models, install Pydantic:

```bash
pip install pydantic
```

Marshmallow continues to work without any additional dependencies.

#### Learn More

- See the [Data Schema](/schema) documentation for comprehensive examples
- Check out the [Pydantic example](/examples) for a complete working application
- All existing marshmallow features continue to work as documented

---

## Migrate to APIFlask 2.x

### Use keyword argument for the `input` data

In APIFlask 2.x, the data passed with the `input` decorator changed
to keyword argument named `{location}_data`. For example, the name
for the JSON input will be `json_data`:

```py
@app.post('/pets')
@app.input(PetQuery, location='query')
@app.input(PetIn)  # equals to app.input(PetIn, location='json')
def create_pet(query_data, json_data):
    pass
```

You can set a custom argument name with `arg_name`:

```py
@app.post('/pets')
@app.input(PetQuery, location='query')
@app.input(PetIn, arg_name='pet')
def create_pet(query_data, pet):
    pass
```


### Replace `/redoc` and `redoc_path` parameter

From APIFlask 2.x, all the OpenAPI docs are available at `/docs`. You can change
the docs UI to ReDoc with the `docs_ui` parameter, and change the docs path
with the `docs_path` parameter:

```py
from apiflask import APIFlask

app = APIFlask(__name__, docs_ui='redoc', docs_path='/redoc')
```


### Replace the `tag` parameter in `@app.doc` with `tags`

The `tag` has removed and `tags` should be used. Always pass a list for `tags`.

```py
@app.doc(tags=['foo'])
```


### Replace the `role` parameter in `@app.auth_required` with `roles`

The `role` has removed and `roles` should be used. Always pass a list for `roles`.

```py
@app.doc(auth_required=['admin'])
```


### Always set the `output(status_code=204)` for 204 response

In APIFlask 2.x, the empty schema has different meanings, and
it won't set the status code to 204.

To return a 204 response, you have to set the status code:

```py
@app.get('/nothing')
@app.output({}, status_code=204)
def nothing():
    return ''
```
