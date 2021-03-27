
![](docs/src/assets/apiflask-logo.png)

# APIFlask

[![Build status](https://github.com/greyli/apiflask/workflows/build/badge.svg)](https://github.com/greyli/apiflask/actions)

APIFlask is a lightweight Python web API framework based on [Flask](https://github.com/pallets/flask/) and [marshmallow-code](https://github.com/marshmallow-code) projects. It's easy to use, high customizable, and 100% compatible with the Flask ecosystem. It starts as a fork of [APIFairy](https://github.com/miguelgrinberg/APIFairy) and inspired by [FastAPI](https://github.com/tiangolo/fastapi).

With APIFlask, you will have:

- More sugars for view function (`@app.get()`, `@app.post()`, `@input()`, `@output()`, `@doc()` and more)
- Automatic request validation and serialization (with [Webargs](https://github.com/marshmallow-code/webargs))
- Automatic response validation and deserialization (with [Marshmallow](https://github.com/marshmallow-code/marshmallow))
- Automatic [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) (OAS, formerly Swagger Specification) document generation (with [APISpec](https://github.com/marshmallow-code/apispec))
- Automatic interactive API documentation (with [Swagger UI](https://github.com/swagger-api/swagger-ui) and [Redoc](https://github.com/Redocly/redoc))
- API Authorization support (with [Flask-HTTPAuth](https://github.com/migulgrinberg/flask-httpauth))
- Automatic JSON response for HTTP errors

*Currently this project is in active development stage, bugs and break changes are expected. Welcome to leave any suggestions or feedbacks in [this issue](https://github.com/greyli/apiflask/issues/1) or just submit a pull request to improve it.*

## Requirements

- Python 3.7+
- Flask 1.1.0+

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

- Website: https://apiflask.com
- Documentation: https://apiflask.com
- PyPI Releases: https://pypi.python.org/pypi/APIFlask
- Change Log: https://apiflask.com/changelog
- Source Code: https://github.com/greyli/apiflask
- Issue Tracker: https://github.com/greyli/apiflask/issues
- Discussion: https://github.com/greyli/apiflask/discussions
- Twitter: https://twitter.com/apiflask

## Example

```python
from apiflask import APIFlask, input, output, Schema, api_abort
from apiflask.fields import Integer, String

app = APIFlask(__name__)

pets = [
    {
        'id': 0,
        'name': 'Kitty',
        'category': 'cat'
    },
    {
        'id': 1,
        'name': 'Coco',
        'category': 'dog'
    }
]


class PetSchema(Schema):
    id = Integer(required=True, dump_only=True)
    name = String(required=True)
    category = String(required=True)


@app.get('/pets/<int:pet_id>')
@output(PetSchema)
def get_pet(pet_id):
    if pet_id > len(pets):
        api_abort(404)
    return pets[pet_id]


@app.post('/pets/<int:pet_id>')
@input(PetSchema)
@output(PetSchema)
def update_pet(pet_id, pet):
    if pet_id > len(pets):
        api_abort(404)
    pet['id'] = pet_id
    pets[pet_id] = pet
    return pet
```

Save the file as `app.py`, then run it with:

```bash
$ flask run
```

Now visit the interactive API documentation (Swagger UI) at <http://localhost:5000/docs>:

![](docs/src/assets/swagger-ui.png)

Or you can visit the alternative API documentation (Redoc) at <http://localhost:5000/redoc>:

![](docs/src/assets/redoc.png)

The auto-generated OpenAPI spec file is available at <http://localhost:5000/openapi.json>.

For a more complete example, see [/examples](https://github.com/greyli/apiflask/tree/master/examples).

## Relationship with Flask

APIFlask is a thin wrapper on top of Flask, you only need to remember two differences:

- When creating an application instance, use `APIFlask` instead of `Flask`.
- When creating a blueprint instance, use `APIBlueprint` instead of `Blueprint`.

For a minimal Flask application:

```python
from flask import Flask, request, escape

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get('name', 'Human')
    return f'Hello, {escape(name)}'
```

Now change to APIFlask:

```python
from apiflask import APIFlask  # step one
from flask import request, escape

app = APIFlask(__name__)  # step two

@app.route('/')
def hello():
    name = request.args.get('name', 'Human')
    return f'Hello, {escape(name)}'
```

In a word, to make Web API development in Flask more easily, APIFlask provided `APIFlask` and `APIBlueprint` to extend Flask's `Flask` and `Blueprint` objects, it also shipped with some helpful utilities. Other than that, you are actually using Flask.
