# Migration Guide

## Migrate to APIFlask 3.x

### Use Pydantic Models

APIFlask 3.x introduces a new schema adapter system that supports both marshmallow schemas and Pydantic models. This change is **fully backward compatible**.

You can now optionally use Pydantic models for type-hint based validation:

```python
from pydantic import BaseModel, Field

class PetIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=30)

@app.input(PetIn)  # Works with the same decorators
def create_pet(json_data):
    return {'message': 'created'}
```

See the [Data Schema](/schema) documentation for comprehensive examples or check out the [Pydantic example](https://github.com/apiflask/apiflask/blob/main/examples/pydantic/app.py) for a complete working application.

!!! important "Output Validation Behavior"

    Unlike marshmallow, **Pydantic validates output data** before sending responses. This means that if your view function returns data that does not conform to the output model schema, a 500 Internal Server Error will be raised.


### Use `security.APIKey*Auth` for API Key Authentication

In APIFlask 3.x, the API key authentication classes have been refactored for better clarity. Instead of using `HTTPTokenAuth` for API key authentication, you should now use one of the following classes based on where the API key is expected:

- `APIKeyHeaderAuth` for API keys in request headers.
- `APIKeyCookieAuth` for API keys in cookies.
- `APIKeyQueryAuth` for API keys in query parameters.

See the [API documentation](/api/security) and the [full example](https://github.com/apiflask/apiflask/blob/main/examples/auth/apikey_auth/app.py) for more details.


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
