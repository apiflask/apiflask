# Migration Guide

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
