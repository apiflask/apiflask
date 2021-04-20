# Migrating from Flask

Since APIFlask is a thin wrapper on top of Flask, you only need to change very little
code to migrating your application to APIFlask (typically less than ten lines of code).

## Change the `Flask` class to the `APIFlask` class

It's how you create the Flask application:

```python
from flask import Flask

app = Flask(__name__)
```

Now change to APIFlask:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
```

## Change `Blueprint` class to `APIBlueprint` class

It's how you create the Flask application:

```python
from flask import Blueprint

bp = Blueprint(__name__, 'foo')
```

Now change to APIFlask:

```python
from apiflask import APIBlueprint

bp = APIBlueprint(__name__, 'foo')
```

!!! tip
    You can register a `Blueprint` object to an `APIFlask` instance. However, you
    can't register an `APIBlueprint` object to a `Flask` instance.

## Update route method (optional)

APIFlask provides some route shortcuts, you can update a view function:

```python hl_lines="1"
@app.route('/pets', methods=['POST'])
def create_pet():
    return {'message': 'created'}
```

to:

```python hl_lines="1"
@app.post('/pets')
def create_pet():
    return {'message': 'created'}
```

!!! tip
    You can mix the use of `app.route()` with route shortcuts. Flask 2.0 will include
    these route shortcuts.

## Other behavior change and notes

### Import statements

You only need to import `APIFlask`, `APIBlueprint`, and other utilities APIFlask
provides from `apiflask` package. For others, you still import them from `flask` package:

```python
from apiflask import APIFlask, APIBlueprint
from flask import request, escape, render_template, g, session, url_for
```

### JSON errors

When you change the base class to `APIFlask`, all the error responses will
automatically convert to JSON format. For example:

```python
from apiflask import APIFlask
from flask import abort

app = APIFlask(__name__)

@app.get('/foo')
def foo():
    abort(404)
```

In the example above, when theuser visit `/foo`, the `abort(400)` will return a JSON
response instead of an HTML error page:

```json
{
    "detail": {},
    "message": "Not Found",
    "status_code": 404
}
```

If you want to disable this behavior, just set `json_errors` to `False`:

```python hl_lines="3"
from apiflask import APIFlask

app = APIFlask(__name__, json_errors=False)
```

Now you can still use `abort_json` from `apiflask` package to return a JSON error
response:

```python hl_lines="3"
from apiflask import APIFlask, abort_json
from flask import abort

app = APIFlask(__name__, json_errors=False)


@app.get('/html-error')
def foo():
    abort(404)


@app.get('/json-error')
def bar():
    abort_json(404)
```

!!! tip
    You can use `message` and `detail` keyword to pass error message and detailed
    information in `abort_json()` function.

### The return values of view function

When you added a `@output` decorator for your view function, notice the
following rules:

- Do not return a `Response` object. You should return a ORM/ODM model object or
a dict that matches the schema you passed in the `@output` decorator.
- You can also return a two-element tuple in the form of `(body, headers)`.

## Next step

Now your application is migrated to APIFlask. Check out the
[Basic Usage](/usage) chapter to learn more about APIFlask. Enjoy!
