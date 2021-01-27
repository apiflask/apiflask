# APIFlask

[![Build status](https://github.com/greyli/apiflask/workflows/build/badge.svg)](https://github.com/greyli/apiflask/actions) [![codecov](https://codecov.io/gh/greyli/apiflask/branch/master/graph/badge.svg)](https://codecov.io/gh/greyli/apiflask)

A lightweight Web API toolkit for Flask, based on marshmallow-code projects and other Flask extensions.

**Currently this project is in plan/experimental stage, break changes are expected. Improvement and suggestions are welcome!**

## Installation

```bash
$ pip install -U apiflask
```

## Example

```python
from flask import Flask
from apiflask import APIFlask
from apiflask.decorators import arguments, body, response
from marshmallow import Schema

app = Flask(__name__)
api = APIFlask(app)


class PetSchema(Schema):
    id = Integer(dump_only=True)
    name = String(required=True)
    age = Integer(required=True)
    category = String(required=True)


@app.route('/pets/<int:pet_id>')
@response(PetSchema)
def get_pet(pet_id):
    pass


@app.route('/pets', methods=['POST'])
@body(PetSchema)
@response(PetSchema)
def create_pet(pet):
    pass


@app.route('/pets', methods=['PUT'])
@body(PetSchema)
@response(PetSchema)
def update_pet(updated_pet, pet_id):
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


## Links

- Documentation (WIP)
- [PyPI](https://pypi.python.org/pypi/APIFlask)
- [Change Log](https://github.com/greyli/apiflask/blob/master/CHANGES.md)

---

APIFlask starts as a fork of [APIFairy 0.6.3dev](https://github.com/miguelgrinberg/APIFairy) and inspired by [FastAPI](https://github.com/tiangolo/fastapi).
