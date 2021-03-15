# APIFlask

[![Build status](https://github.com/greyli/apiflask/workflows/build/badge.svg)](https://github.com/greyli/apiflask/actions)

A lightweight Python 3.7+ Web API framework, based on Flask, marshmallow-code projects and other Flask extensions.

![](images/apiflask-logo.png)

WARNING: Currently this project is in experimental and active development stage, bugs and break changes are expected. Improvements and suggestions are welcome!

## Installation

```bash
$ pip install apiflask
```

## Example

```python
from apiflask import APIFlask, input, output, Schema
from apiflask.fields import Integer, String

app = APIFlask(__name__)


class PetQuerySchema(Schema):
    query = String(required=True)


class PetSchema(Schema):
    id = Integer(dump_only=True)
    name = String(required=True)
    age = Integer(required=True)
    category = String(required=True)


@app.get('/pets/<int:pet_id>')
@output(PetSchema)
def get_pet(pet_id):
    pass


@app.post('/pets')
@input(PetQuerySchema, location='query')
@input(PetSchema)
@output(PetSchema)
def create_pet(query, pet):
    pass


@app.put('/pets/<int:pet_id>')
@input(PetSchema)
@output(PetSchema)
def update_pet(pet_id, updated_pet):
    pass
```

Save the file as `app.py`, then run it with:

```bash
$ flask run
``` 

Now visit the interactive docs by Swagger UI at <http://localhost:5000/docs>:

![](./images/swaggerui.png)

Or you can visit the alternative Redoc docs at <http://localhost:5000/redoc>:

![](./images/redoc.png)

The auto-generated OpenAPI spec file are available at <http://localhost:5000/openapi.json>.


## Features

- More sugars for view function (@app.get, @app.post, @input, @output, etc.)
- Automatic request and response validatation and de/serilazation
- Automatci OpenAPI spec generation
- Automatic API documentation with Swagger UI and Redoc
- Automatic JSON response for errors
- Pagination support (WIP)
- Async support (WIP)
- GraphQL support (WIP)
- And more features lied in my todo list :)

## Links

- Homepage (WIP)
- Documentation (5%)
- [PyPI](https://pypi.python.org/pypi/APIFlask)
- [Change Log](https://github.com/greyli/apiflask/blob/master/CHANGES.md)

## Contribution

- Vote for your favorite name of function/decorator/class.
- Propose or vote the your desired feature.

## Todo

- A better Logo (HELP NEEDED)

---

APIFlask starts as a fork of [APIFairy 0.6.3dev](https://github.com/miguelgrinberg/APIFairy) and inspired by [FastAPI](https://github.com/tiangolo/fastapi).
