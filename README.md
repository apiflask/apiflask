
![](https://apiflask.com/_assets/apiflask-logo.png)

# APIFlask

[![Build status](https://github.com/greyli/apiflask/workflows/build/badge.svg)](https://github.com/greyli/apiflask/actions) [![codecov](https://codecov.io/gh/greyli/apiflask/branch/main/graph/badge.svg?token=2CFPCZ1DMY)](https://codecov.io/gh/greyli/apiflask)

APIFlask is a lightweight Python web API framework based on [Flask](https://github.com/pallets/flask) and [marshmallow-code](https://github.com/marshmallow-code) projects. It's easy to use, highly customizable, ORM/ODM-agnostic, and 100% compatible with the Flask ecosystem. It starts as a fork of [APIFairy](https://github.com/miguelgrinberg/APIFairy) and is inspired by [flask-smorest](https://github.com/marshmallow-code/flask-smorest) and [FastAPI](https://github.com/tiangolo/fastapi) (see *[Comparison and Motivations](https://apiflask.com/comparison)* for the comparison between these projects).

With APIFlask, you will have:

- More sugars for view function (`@input()`, `@output()`, `@app.get()`, `@app.post()` and more)
- Automatic request validation and deserialization (with [Webargs](https://github.com/marshmallow-code/webargs))
- Automatic response formatting and serialization (with [Marshmallow](https://github.com/marshmallow-code/marshmallow))
- Automatic [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification) (OAS, formerly Swagger Specification) document generation (with [APISpec](https://github.com/marshmallow-code/apispec))
- Automatic interactive API documentation (with [Swagger UI](https://github.com/swagger-api/swagger-ui) and [Redoc](https://github.com/Redocly/redoc))
- API authentication support (with [Flask-HTTPAuth](https://github.com/migulgrinberg/flask-httpauth))
- Automatic JSON response for HTTP errors


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

- Website: <https://apiflask.com>
- Documentation: <https://apiflask.com/docs>
- PyPI Releases: <https://pypi.python.org/pypi/APIFlask>
- Change Log: <https://apiflask.com/changelog>
- Source Code: <https://github.com/greyli/apiflask>
- Issue Tracker: <https://github.com/greyli/apiflask/issues>
- Discussion: <https://github.com/greyli/apiflask/discussions>
- Twitter: <https://twitter.com/apiflask>


## Example

```python
from apiflask import APIFlask, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'}
]


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/')
def say_hello():
    # returning a dict equals to use jsonify()
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    # you can also return an ORM/ODM model class instance directly
    # APIFlask will serialize the object into JSON format
    return pets[pet_id]


@app.patch('/pets/<int:pet_id>')
@input(PetInSchema(partial=True))
@output(PetOutSchema)
def update_pet(pet_id, data):
    # the validated and parsed input data will
    # be injected into the view function as a dict
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]
```

<details>
<summary>You can also use class-based views with <code>MethodView</code></summary>

```python
from apiflask import APIFlask, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask.views import MethodView

app = APIFlask(__name__)

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'}
]


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


# use the "route" decorator to decorate the view class
@app.route('/')
class Hello(MethodView):

    # use HTTP method name as class method name
    def get(self):
        return {'message': 'Hello!'}


@app.route('/pets/<int:pet_id>')
class Pet(MethodView):

    @output(PetOutSchema)
    def get(self, pet_id):
        """Get a pet"""
        if pet_id > len(pets) - 1:
            abort(404)
        return pets[pet_id]

    @input(PetInSchema(partial=True))
    @output(PetOutSchema)
    def patch(self, pet_id, data):
        """Update a pet"""
        if pet_id > len(pets) - 1:
            abort(404)
        for attr, value in data.items():
            pets[pet_id][attr] = value
        return pets[pet_id]
```
</details>

<details>
<summary>Or use <code>async def</code> with Flask 2.0</summary>

```bash
$ pip install -U flask[async]
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

Save this as `app.py`, then run it with :

```bash
$ flask run --reload
```

Now visit the interactive API documentation (Swagger UI) at <http://localhost:5000/docs>:

![](https://apiflask.com/_assets/swagger-ui.png)

Or you can visit the alternative API documentation (Redoc) at <http://localhost:5000/redoc>:

![](https://apiflask.com/_assets/redoc.png)

The auto-generated OpenAPI spec file is available at <http://localhost:5000/openapi.json>. You can also get the spec with [the `flask spec` command](https://apiflask.com/openapi/#the-flask-spec-command):

```bash
$ flask spec
```

For some complete examples, see [/examples](https://github.com/greyli/apiflask/tree/main/examples).


## Relationship with Flask

APIFlask is a thin wrapper on top of Flask. You only need to remember four differences (see *[Migrating from Flask](https://apiflask.com/migrating)* for more details):

- When creating an application instance, use `APIFlask` instead of `Flask`.
- When creating a blueprint instance, use `APIBlueprint` instead of `Blueprint`.
- The `abort()` function from APIFlask (`apiflask.abort`) returns JSON error response.
- The view class should be registered with the `route` decorator.

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

In a word, to make Web API development in Flask more easily, APIFlask provides `APIFlask` and `APIBlueprint` to extend Flask's `Flask` and `Blueprint` objects and it also ships with some helpful utilities. Other than that, you are actually using Flask.
