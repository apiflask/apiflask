# Schema, Fields, and Validators


## Schema name resolver

!!! warning "Version >= 0.9.0"

    This feature was added in the [version 0.9.0](/changelog/#version-090).

The OpenAPI schema name of each schema is resolved based on a resolver function, here is
the default schema name resolver used in APIFlask:

```python
def schema_name_resolver(schema):
    name = schema.__class__.__name__  # get schema class name
    if name.endswith('Schema'):  # remove the "Schema" suffix
        name = name[:-6] or name
    if schema.partial:  # add a "Update" suffix for partial schema
        name += 'Update'
    return name
```

You can provide a custom schema name resolver by setting the `APIFlask.schema_name_resolver`
attribute:

```python hl_lines="14"
from apiflask import APIFlask


def my_schema_name_resolver(schema):
    name = schema.__class__.__name__
    if name.endswith('Schema'):
        name = name[:-6] or name
    if schema.partial:
        name += 'Partial'
    return name


app = APIFlask(__name__)
app.schema_name_resolver = my_schema_name_resolver
```

The schema name resolver should accept the schema object as argument and return the name.


## Base response schema customization

!!! warning "Version >= 0.9.0"

    This feature was added in the [version 0.9.0](/changelog/#version-090).

When you set up the output of a view function with the `output` decorator, you need to
return the object or dict that matches the schema you passed to the `output` decorator. Then,
APIFlask will serialize the return value to response body:

```python
{
    "id": 2,
    "name": "Kitty",
    "category": "cat"
}
```

However, You may want to insert the output data into a data field and add some meta fields.
So that you can return a unified response for all endpoints. For example, make all the
responses to the following format:

```python
{
    "data": {
        "id": 2,
        "name": "Kitty",
        "category": "cat"
    },
    "message": "some message",
    "status_code": "custom code"
}
```

To achieve this, you will need to set a base response schema, then pass it to the configuration variable
`BASE_RESPONSE_SCHEMA`:

```python
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field

app = APIFlask(__name__)

class BaseResponseSchema(Schema):
    message = String()
    status_code = Integer()
    data = Field()  # the data key

app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
```

The default data key is "data", you can change it to match your data field name in your schema
via the configuration variable `BASE_RESPONSE_DATA_KEY`:

```python
app.config['BASE_RESPONSE_DATA_KEY '] = 'data'
```

Now you can return a dict matches the base response schema in your view functions:

```python
@app.get('/')
def say_hello():
    data = {'name': 'Grey'}
    return {'message': 'Success!', 'status_code': 200, 'data': data}
```

To make it more elegant, you can create a function to make response dict:

```python
def make_resp(message, status_code, data):
    return {'message': message, 'status_code': status_code, 'data': data}


@app.get('/')
def say_hello():
    data = {'message': 'Hello!'}
    return make_resp('Success!', 200, data)


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return make_resp('Success!', 200, pets[pet_id])
```

Check out [the complete example application](https://github.com/greyli/apiflask/tree/main/examples/base_response/app.py)
for more details, see [the examples page](/examples) for running the example application.
