
![](https://apiflask.com/_assets/apiflask-logo.png)

# APIFlask

[![Build status](https://github.com/apiflask/apiflask/actions/workflows/tests.yml/badge.svg)](https://github.com/apiflask/apiflask/actions) [![codecov](https://codecov.io/gh/apiflask/apiflask/branch/main/graph/badge.svg?token=2CFPCZ1DMY)](https://codecov.io/gh/apiflask/apiflask)

APIFlask is a lightweight Python web API framework based on [Flask](https://github.com/pallets/flask). It's easy to use, highly customizable, ORM/ODM-agnostic, and 100% compatible with the Flask ecosystem.

APIFlask supports both [marshmallow](https://github.com/marshmallow-code/marshmallow) schemas and [Pydantic](https://docs.pydantic.dev/) models through a pluggable schema adapter system, giving you the flexibility to choose the validation approach that best fits your project.

With APIFlask, you will have:

- More sugars for view function (`@app.input()`, `@app.output()`, `@app.get()`, `@app.post()` and more)
- Automatic request validation and deserialization
- Automatic response formatting and serialization
- Automatic [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) (OAS, formerly Swagger Specification) document generation
- Automatic interactive API documentation
- API authentication support (with [Flask-HTTPAuth](https://github.com/miguelgrinberg/flask-httpauth))
- Automatic JSON response for HTTP errors


## Requirements

- Python 3.9+
- Flask 2.1+


## Installation

For Linux and macOS:

```bash
$ pip3 install apiflask
```

For Windows:

```bash
> pip install apiflask
```


## Links

- Website: <https://apiflask.com>
- Documentation: <https://apiflask.com/docs>
- 中文文档: <https://zh.apiflask.com/docs>
- PyPI Releases: <https://pypi.python.org/pypi/APIFlask>
- Change Log: <https://apiflask.com/changelog>
- Source Code: <https://github.com/apiflask/apiflask>
- Issue Tracker: <https://github.com/apiflask/apiflask/issues>
- Discussion: <https://github.com/apiflask/apiflask/discussions>
- 中文论坛: <https://codekitchen.community>
- Twitter: <https://twitter.com/apiflask>
- Open Collective: <https://opencollective.com/apiflask>


## Donate

If you find APIFlask useful, please consider [donating](https://opencollective.com/apiflask) today. Your donation keeps APIFlask maintained and evolving.

Thank you to all our backers and sponsors!

### Backers

[![](https://opencollective.com/apiflask/backers.svg?width=890)](https://opencollective.com/apiflask)

### Sponsors

[![](https://opencollective.com/apiflask/sponsors.svg?width=890)](https://opencollective.com/apiflask)

## Example

```python
from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'}
]


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/')
def say_hello():
    # returning a dict or list equals to use jsonify()
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    # you can also return an ORM/ODM model class instance directly
    # APIFlask will serialize the object into JSON format
    return pets[pet_id]


@app.patch('/pets/<int:pet_id>')
@app.input(PetIn(partial=True))  # -> json_data
@app.output(PetOut)
def update_pet(pet_id, json_data):
    # the validated and parsed input data will
    # be injected into the view function as a dict
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in json_data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]
```

<details>
<summary>You can use Pydantic models for type-hint based validation</summary>

```python
from enum import Enum

from apiflask import APIFlask, abort
from pydantic import BaseModel, Field

app = APIFlask(__name__)


class PetCategory(str, Enum):
    DOG = 'dog'
    CAT = 'cat'


class PetOut(BaseModel):
    id: int
    name: str
    category: PetCategory


class PetIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    category: PetCategory


pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'}
]


@app.get('/')
def say_hello():
    return {'message': 'Hello, Pydantic!'}


@app.get('/pets')
@app.output(list[PetOut])
def get_pets():
    return pets


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id: int):
    if pet_id > len(pets) or pet_id < 1:
        abort(404)
    return pets[pet_id - 1]


@app.post('/pets')
@app.input(PetIn, location='json')
@app.output(PetOut, status_code=201)
def create_pet(json_data: PetIn):
    # the validated and parsed input data will
    # be injected into the view function as a Pydantic model instance
    new_id = len(pets) + 1
    new_pet = PetOut(id=new_id, name=json_data.name, category=json_data.category)
    pets.append(new_pet)
    return new_pet
```

</details>

<details>
<summary>Or use <code>async def</code></summary>

```bash
$ pip install -U "apiflask[async]"
```

```python
import asyncio

from apiflask import APIFlask

app = APIFlask(__name__)


@app.get('/')
async def say_hello():
    await asyncio.sleep(1)
    return {'message': 'Hello!'}
```

See <em><a href="https://flask.palletsprojects.com/async-await">Using async and await</a></em> for the details of the async support in Flask 2.0.

</details>

Save this as `app.py`, then run it with:

```bash
$ flask run --debug
```

Now visit the interactive API documentation (Swagger UI) at <http://localhost:5000/docs>:

![](https://apiflask.com/_assets/swagger-ui.png)

Or you can change the API documentation UI when creating the APIFlask instance with the `docs_ui` parameter:

```py
app = APIFlask(__name__, docs_ui='redoc')
```

Now <http://localhost:5000/docs> will render the API documentation with Redoc.

Supported `docs_ui` values (UI libraries) include:

- `swagger-ui` (default value): [Swagger UI](https://github.com/swagger-api/swagger-ui)
- `redoc`: [Redoc](https://github.com/Redocly/redoc)
- `elements`: [Elements](https://github.com/stoplightio/elements)
- `rapidoc`: [RapiDoc](https://github.com/rapi-doc/RapiDoc)
- `rapipdf`: [RapiPDF](https://github.com/mrin9/RapiPdf)

The auto-generated OpenAPI spec file is available at <http://localhost:5000/openapi.json>. You can also get the spec with [the `flask spec` command](https://apiflask.com/openapi/#the-flask-spec-command):

```bash
$ flask spec
```

For some complete examples, see [/examples](https://github.com/apiflask/apiflask/tree/main/examples).


## Relationship with Flask

APIFlask is a thin wrapper on top of Flask. You only need to remember the following differences (see *[Migrating from Flask](https://apiflask.com/migrations/flask/)* for more details):

- When creating an application instance, use `APIFlask` instead of `Flask`.
- When creating a blueprint instance, use `APIBlueprint` instead of `Blueprint`.
- The `abort()` function from APIFlask (`apiflask.abort`) returns JSON error response.

For a minimal Flask application:

```python
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get('name', 'Human')
    return f'Hello, {escape(name)}'
```

Now change to APIFlask:

```python
from apiflask import APIFlask  # step one
from flask import request
from markupsafe import escape

app = APIFlask(__name__)  # step two

@app.route('/')
def hello():
    name = request.args.get('name', 'Human')
    return f'Hello, {escape(name)}'
```

In a word, to make Web API development in Flask more easily, APIFlask provides `APIFlask` and `APIBlueprint` to extend Flask's `Flask` and `Blueprint` objects and it also ships with some helpful utilities. Other than that, you are actually using Flask.


## Credits

APIFlask starts as a fork of [APIFairy](https://github.com/miguelgrinberg/APIFairy) and is inspired by [flask-smorest](https://github.com/marshmallow-code/flask-smorest) and [FastAPI](https://github.com/tiangolo/fastapi) (see *[Comparison and Motivations](https://apiflask.com/comparison)* for the comparison between these projects).
