# Response Formatting

Read the following sections in the Basic Usage chapter first for the basics on response formatting:

- [Use `@app.output` to format response data](/usage/#use-appoutput-to-format-response-data)
- [The return value of the view function](/usage/#the-return-value-of-the-view-function)

Basic concepts on response formatting:

- APIFlask uses [marshmallow](https://github.com/marshmallow-code/marshmallow) to handle
  the response formatting.
- The response data returned by the view function will only be formatting against your
  schema, not validating.
- You can only declare one output (use one `app.output` decorator) for the JSON response body.
- The error responses of your view can be declared with `app.doc(response=...)`.


## Pagination support

APIFlask provides two utilies for pagination:

- [apiflask.PaginationSchema](/api/schemas/#apiflask.schemas.PaginationSchema)
- [apiflask.pagination_builder](/api/helpers/#apiflask.helpers.pagination_builder)

The `PaginationSchema` is a schema that contains the general fields
for pagination information.

The `pagination_builder` is a helper function to generate pagination
data for the `PaginationSchema`.

To add pagination support to our pet store example. First, we create a
schema for query strings:

```python
from apiflask import Schema
from apiflask.fields import Integer
from apiflask.validators import Range


class PetQuery(Schema):
    page = Integer(load_default=1)  # set default page to 1
    # set default value to 20, and make sure the value is less than 30
    per_page = Integer(load_default=20, validate=Range(max=30))
```

Then we create a pet output schema, and a pets schema that contains
a list of nested `PetOut` schema, and a nested `PaginationSchema`
schema.

```python
from apiflask import Schema, PaginationSchema
from apiflask.fields import Integer, String, List, Nested


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()


class PetsOut(Schema):
    pets = List(Nested(PetOut))
    pagination = Nested(PaginationSchema)
```

Now we use these schemas in our `get_pets` view:

```python
from apiflask import APIFlask, pagination_builder


@app.get('/pets')
@app.input(PetQuery, location='query')
@app.output(PetsOut)
def get_pets(query):
    pagination = PetModel.query.paginate(
        page=query['page'],
        per_page=query['per_page']
    )
    pets = pagination.items
    return {
        'pets': pets,
        'pagination': pagination_builder(pagination)
    }
```

In the return value of the view function, we use `pagination_builder`
to build the pagination data and passes the `pagination` object provided
by Flask-SQLAlchemy.

This function is designed based on Flask-SQLAlchemy's `Pagination` class.
If you are using a different or custom pagination class, make sure the
passed pagination object has the following attributes:

- `page`
- `per_page`
- `pages`
- `total`
- `next_num`
- `has_next`
- `prev_num`
- `has_prev`

You can also write a custom builder function and pagination schema
to build your custom pagination data.

See the [full example](https://github.com/apiflask/apiflask/blob/main/examples/pagination/app.py)
for more details.


## Response examples

You can set response examples for OpenAPI spec with the `example` and `examples`
parameters, see [this section](/openapi/#response-and-request-example) in the
OpenAPI Generating chapter for more details.


## Dict schema

When passing the schema to `app.output`, you can also use a dict instead of a schema class:

```python
from apiflask.fields import Integer


@app.get('/')
@app.output({'answer': Integer(dump_default=42)})
def get_answer():
    return {'answer': 'Nothing'}
```

The dict schema's name will be something like `"Generated"`. To specify a schema
name, use the `schema_name` parameter:

```python
from apiflask.fields import Integer


@app.get('/')
@app.output({'answer': Integer(dump_default=42)}, schema_name='Answer')
def get_answer():
    return {'answer': 'Nothing'}
```

However, we recommend creating a schema class whenever possible to make the
code easy to read and reuse.
