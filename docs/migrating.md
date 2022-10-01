# Migrating from Flask

Since APIFlask is a thin wrapper on top of Flask, you only need to change very little
code to migrating your application to APIFlask (typically less than ten lines of code).


## `Flask` class -> `APIFlask` class

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


## `Blueprint` class -> `APIBlueprint` class

It's how you create the Flask application:

```python
from flask import Blueprint

bp = Blueprint('foo', __name__)
```

Now change to APIFlask:

```python
from apiflask import APIBlueprint

bp = APIBlueprint('foo', __name__)
```

!!! tip

    You can register a `Blueprint` object to an `APIFlask` instance, but you
    can't register an `APIBlueprint` object to a `Flask` instance.


## Use route shortcuts (optional)

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


## Class-based views (MethodView)

!!! warning "Version >= 0.5.0"

    This feature was added in the [version 0.5.0](/changelog/#version-050).

APIFlask support to use the `MethodView`-based view class, for example:

```python
from apiflask import APIFlask, Schema, input, output
from flask.views import MethodView

# ...

class Pet(MethodView):

    decorators = [doc(responses=[404])]

    @app.output(PetOut)
    def get(self, pet_id):
        pass

    @app.output({}, status_code=204)
    def delete(self, pet_id):
        pass

    @app.input(PetIn)
    @app.output(PetOut)
    def put(self, pet_id, data):
        pass

    @app.input(PetIn(partial=True))
    @app.output(PetOut)
    def patch(self, pet_id, data):
        pass

app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
```

The `View`-based view class is not supported, you can still use it but currently
APIFlask can't generate OpenAPI spec (and API documentation) for it.


## Other behavior changes and notes


### Import statements

You only need to import `APIFlask`, `APIBlueprint`, and other utilities APIFlask
provides from the `apiflask` package. For others, you still import them from
the `flask` package:

```python
from apiflask import APIFlask, APIBlueprint
from flask import request, escape, render_template, g, session, url_for
```


### APIFlask's `abort()` vs Flask's `abort()`

APIFlask's `abort()` function will return a JSON error response while Flask's `abort()`
returns an HTML error page:

```python
from apiflask import APIFlask, abort

app = APIFlask(__name__)

@app.get('/foo')
def foo():
    abort(404)
```

In the example above, when the user visits `/foo`, the response body will be:

```json
{
    "detail": {},
    "message": "Not Found",
    "status_code": 404
}
```

You can use `message` and `detail` parameter to pass error message and detailed
information in the `abort()` function.

!!! warning

    The function `abort_json()` was renamed to `abort()` in the
    [version 0.4.0](/changelog/#version-040).


### JSON errors and mix the use of `flask.abort()` and `apiflask.abort()`

When you change the base application class to `APIFlask`, all the error responses
will automatically convert to JSON format even if you use Flask's `abort()` function:

```python
from apiflask import APIFlask
from flask import abort

app = APIFlask(__name__)

@app.get('/foo')
def foo():
    abort(404)
```

If you want to disable this behavior, just set `json_errors` parameter to `False`:

```python hl_lines="3"
from apiflask import APIFlask

app = APIFlask(__name__, json_errors=False)
```

Now you can still use `abort` from `apiflask` package to return a JSON error
response. To mix the use of `flask.abort` and `apiflask.abort`, you will need
to import one of them with a different name:

```python
from apiflask import abort as abort_json
```

Here is a full example:

```python hl_lines="1 14"
from apiflask import APIFlask, abort as abort_json
from flask import abort

app = APIFlask(__name__, json_errors=False)


@app.get('/html-error')
def foo():
    abort(404)


@app.get('/json-error')
def bar():
    abort_json(404)
```


### The return values of view function

For a simple view function without `@app.output` decorator, you can return a dict or
a list as JSON response. The returned dict and list will be converted to a JSON
response automatically (by calling
[`jsonify()`](https://flask.palletsprojects.com/api/#flask.json.jsonify) underly).

!!! tip

    Although list looks like tuple, only list return values will be serialized to JSON
    response. Tuple has
    [special meaning](https://flask.palletsprojects.com/quickstart/#about-responses).

    Starting from Flask 2.2, the list return values are supported natively.

```python
@app.get('/foo')
def foo():
    return {'message': 'foo'}


@app.get('/bar')
def bar():
    return ['foo', 'bar', 'baz']
```

When you added a `@app.output` decorator for your view function, APIFlask expects you to
return an ORM/ODM model object or a dict/list that matches the schema you passed in the
`@app.output` decorator. If you return a `Response` object, APIFlask will return it
directly without any process.


## Next step

Now your application is migrated to APIFlask. Check out the
[Basic Usage](/usage) chapter to learn more about APIFlask. Enjoy!
