# Data Schema

Read [this section](/usage/#use-appinput-to-validate-and-deserialize-request-data) and following
section first in the Basic Usage chapter for the basics of writing input and output schema.

Basic concepts on data schema:

- APIFlask schema = [marshmallow](https://github.com/marshmallow-code/marshmallow) schema.
- APIFlask's `apiflask.Schema` base class is directly imported from marshmallow, see the
  [API documentation](https://marshmallow.readthedocs.io/en/stable/marshmallow.schema.html)
  for the details.
- We recommend separating input and output schema. Since the output data is not
  validated, you don't need to define validators on output fields.
- `apiflask.fields` includes all the fields provided by marshmallow, webargs, and
  flask-marshmallow (while some aliases were removed).
- `apiflask.validators` includes all the validators in `marshmallow.validate`.
- For other functions/classes, just import them from marshmallow.
- Read [marshmallow's documentation](https://marshmallow.readthedocs.io/) when you have free time.


## Deserialization (load) and serialization (dump)

In APIFlask (marshmallow), the process of parsing and validating the input request data
is called deserialization (we **load** the data from the request). And the process of
formatting the output response data is called serialization (we **dump** the data to
the response).

Notice we use the "load" and "dump" to represent these two processes. When creating
the schema, we set the default value for the fields in the input schema with the `load_default`
parameter, and we use the `dump_default` parameter to set the default value for fields
in the output schema.

There are four decorators to register callback methods in the load/dump processes:

- `pre_load`: to register a method to invoke before parsing/validating the request data
- `post_load`: to register a method to invoke after parsing/validating the request data
- `pre_dump`: to register a method to invoke before formatting the return value of the view function
- `post_dump`: to register a method to invoke after formatting the return value of the view function

And there are two decorators to register a validation method:

- `validates(field_name)`: to register a method to validate a specified field
- `validates_schema`: to register a method to validate the whole schema

!!! tip

    When using the `validates_schema`, notice the `skip_on_field_errors` is set to `True` as default:
    > If skip_on_field_errors=True, this validation method will be skipped whenever validation errors
    > have been detected when validating fields.

Import these decorators directly from marshmallow:

```python
from marshmallow import pre_load, post_dump, validates
```

See [this chapter](https://marshmallow.readthedocs.io/en/stable/extending.html) and the
[API documentation](https://marshmallow.readthedocs.io/en/stable/marshmallow.decorators.html)
of these decorators for the details.


## Data fields

APIFlask's `apiflask.fields` module includes all the data fields from marshmallow, webargs, and
Flask-Marshmallow. We recommend importing them from the `apiflask.fields` module:

```python
from apiflask.fields import String, Integer
```

Or you prefer to keep a reference:

```python
from apiflask import Schema, fields

class FooBar(Schema):
    foo = fields.String()
    bar = fields.Integer()
```

!!! warning "Some field aliases were removed"

    The following field aliases were removed:

    - `Str`
    - `Int`
    - `Bool`
    - `Url`
    - `UrlFor`
    - `AbsoluteUrlFor`

    Instead, you will need to use:

    - `String`
    - `Integer`
    - `Boolean`
    - `URL`
    - `URLFor`
    - `AbsoluteURLFor`

    See [apiflask#63](https://github.com/apiflask/apiflask/issues/63) and
    [marshmallow#1828](https://github.com/marshmallow-code/marshmallow/issues/1828)for more details.


### marshmallow fields

API documentation: <https://marshmallow.readthedocs.io/en/stable/marshmallow.fields.html>

- `AwareDateTime`
- `Boolean`
- `Constant`
- `Date`
- `DateTime`
- `Decimal`
- `Dict`
- `Email`
- `Field`
- `Float`
- `Function`
- `Integer`
- `IP`
- `IPv4`
- `IPv6`
- `List`
- `Mapping`
- `Method`
- `NaiveDateTime`
- `Nested`
- `Number`
- `Pluck`
- `Raw`
- `String`
- `Time`
- `TimeDelta`
- `Tuple`
- `URL`
- `UUID`


## Flask-Marshmallow fields

API documentation: <https://flask-marshmallow.readthedocs.io/en/latest/#flask-marshmallow-fields>

- `AbsoluteURLFor`
- `Hyperlinks`
- `URLFor`


## webargs fields

API documentation: <https://webargs.readthedocs.io/en/latest/api.html#module-webargs.fields>

- `DelimitedList`
- `DelimitedTuple`


## APIFlask fields

API documentation: <https://apiflask.com/api/fields/#apiflask.fields.File>

- `File`

!!! tip

    If the existing fields don't fit your needs, you can also create
    [custom fields](https://marshmallow.readthedocs.io/en/stable/custom_fields.html).


## Data validators

APIFlask's `aipflask.validators` contains all the validator class provided by marshmallow:

- `ContainsNoneOf`
- `ContainsOnly`
- `Email`
- `Equal`
- `Length`
- `NoneOf`
- `OneOf`
- `Predicate`
- `Range`
- `Regexp`
- `URL`
- `Validator`

See the [API documentation](https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html)
for the detailed usage.

When specifying validators for a field, you can pass a single validator to the `validate` parameter:

```python
from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import OneOf


class PetIn(Schema):
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

Or pass a list of validators:

```python
from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length, OneOf


class PetIn(Schema):
    category = String(required=True, validate=[OneOf(['dog', 'cat']), Length(0, 10)])
```

!!! tip

    If the existing validators don't fit your needs, you can also create
    [custom validators](https://marshmallow.readthedocs.io/en/stable/quickstart.html#validation).


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
    "code": "custom code"
}
```

To achieve this, you will need to set a base response schema, then pass it to the configuration variable
`BASE_RESPONSE_SCHEMA`:

```python
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field

app = APIFlask(__name__)

class BaseResponse(Schema):
    data = Field()  # the data key
    message = String()
    code = Integer()

app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse
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
    return {
        'data': data,
        'message': 'Success!',
        'code': 200
    }
```

Check out [the complete example application](https://github.com/apiflask/apiflask/tree/main/examples/base_response/app.py)
for more details, see [the examples page](/examples) for running the example application.


## Use dataclass as data schema

With [marshmalow-dataclass](https://github.com/lovasoa/marshmallow_dataclass), you can define
dataclasses and then convert them into marshmallow schemas.

```bash
$ pip install marshmallow-dataclass
```

You can use the `dataclass` decorator from marshmallow-dataclass to create the data class, then call the
`.Schema` attribute to get the corresponding marshmallow schema:

```python
from dataclasses import field

from apiflask import APIFlask
from apiflask.validators import Length, OneOf
from marshmallow_dataclass import dataclass


app = APIFlask(__name__)


@dataclass
class PetIn:
    name: str = field(
        metadata={'required': True, 'validate': Length(min=1, max=10)}
    )
    category: str = field(
        metadata={'required': True, 'validate': OneOf(['cat', 'dog'])}
    )


@dataclass
class PetOut:
    id: int
    name: str
    category: str


@app.post('/pets')
@app.input(PetIn.Schema)
@app.output(PetOut.Schema, status_code=201)
def create_pet(pet: PetIn):
    return {
        'id': 0,
        'name': pet.name,
        'category': pet.category
    }
```

Check out [the complete example application](https://github.com/apiflask/apiflask/tree/main/examples/dataclass/app.py)
for more details, see [the examples page](/examples) for running the example application.

Read [mashmallow-dataclass's documentation](https://lovasoa.github.io/marshmallow_dataclass/html/marshmallow_dataclass.html)
and [dataclasses](https://docs.python.org/3/library/dataclasses.html) for more information.
