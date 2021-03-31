# Basic Usage

This chapter will cover the basic usage of APIFlask.

## Installation

=== "Linux/macOS"

    ```
    $ pip3 install apiflask
    ```

=== "Windows"

    ```
    > pip install apiflask
    ```

!!! tip "Python dependency managament tools"
    The command above use [pip](_pip) to install APIFlask, you can also use other dependency
    managament tools such as [Poetry](_poetry), [Pipenv](_pipenv), [PDM](_pdm), etc.

    [_pip]: https://pip.pypa.io/
    [_poetry]: https://python-poetry.org/
    [_pipenv]: https://pipenv.pypa.io/
    [_pdm]: https://pdm.fming.dev/

## Creating an `app` instance with `APIFlask`

Similar to what you did to create a Flask `app` instance, you will need to import
`APIFlask` from `apiflask` package:

```python
from apiflask import APIFlask

app = APIFlask(__name__)


@app.route('/')
def index():
    return {'message': 'hello'}
```

The default title and version of the API will be `APIFlask` and `0.1.0`, you can 
pass the `title` and the `version` arguments to change these settings:

```python
app = APIFlask(__name__, title='Wonderful API', version='1.0')
```

To run this application, you can save it as `app.py`, then run the `flask run` command:

```bash
$ flask run
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

If you want to make the application restart whenever the code changes, you can enable
reloader with `--reload` option:

```bash
$ flask run --reload
```

!!! tip
    Install `watchdog` for a better performance for the application reloader:

    === "Linux/macOS"

        ```
        $ pip3 install watchdog
        ```

    === "Windows"

        ```
        > pip install watchdog
        ```

I highly recommend to enable "debug mode" when develop Flask application, see the note below
for the details.

??? note "Enabling the debug mode"

    Flask can automatically restart and reload the application when code changes and display useful debug information for errors. To enable these features in your Flask application, we will need to set the environment variable `FLASK_ENV` to `development.`

    === "Bash"

        ```
        $ export FLASK_ENV=development
        ```
    
    === "Windows CMD"

        ```
        > set FLASK_ENV=development
        ```

    === "Powershell"

        ```
        > $env:FLASK_APP="development"
        ```

    For a proper Flask application setup, we normally store the environment variables into a file called
    `.flaskenv` (which is used to store Flask-specific environment variables):
    
    ```
    # save as .flaskenv
    FLASK_ENV=development
    ```

    then install `python-dotenv`:

    === "Linux/macOS"

        ```
        $ pip3 install python-dotenv
        ```

    === "Windows"

        ```
        > pip install python-dotenv
        ```

    Now when you run `flask run`, the application starts in debug mode:

    ```
    $ flask run
     * Environment: development
     * Debug mode: on
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 101-750-099
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

## Interactive API documentation

Once you have created the app instace, the interactive API documentation will be availabe 
at <http://localhost:5000/docs> and <http://localhost:5000/redoc>. On top of that,
the OpenAPI spec file will be available at <http://localhost:5000/openapi.json>.

You can refresh the documentation whenever you added a new route or added the input and output
definition for the view function in the following sections.

## Create a route with route decorators

To create a view function, you can do exactly what you did with Flask:

```python
from apiflask import APIFlask

app = APIFlask(__name__)


@app.route('/')
def index():
    return {'message': 'hello'}


@app.route('/pets/<int:pet_id>')
def get_pet(pet_id):
    return {'message': 'OK'}


@app.route('/pets')
def get_pets():
    return {'message': 'OK'}


@app.route('/pets', methods=['POST'])
def create_pet():
    return {'message': 'created'}, 201


@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    return {'name': 'updated'}


@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    return '', 204
```

With APIFlask, instead of setting `methods` argument for each route, you can use the following
shortcuts decorators:

- `app.get()`: register a route which only accepts *GET* request.
- `app.post()`: register a route which only accepts *POST* request.
- `app.put()`: register a route which only accepts *PUT* request.
- `app.patch()`: register a route which only accepts *PATCH* request.
- `app.delete()`: register a route which only accepts *DELETE* request.

This is the same example with the route shortcuts:

```python hl_lines="6 11 16 21 26 31"
from apiflask import APIFlask

app = APIFlask(__name__)


@app.get('/')
def index():
    return {'message': 'hello'}


@app.get('/pets/<int:pet_id>')
def get_pet(pet_id):
    return {'message': 'OK'}


@app.get('/pets')
def get_pets():
    return {'message': 'OK'}


@app.post('/pets')
def create_pet():
    return {'message': 'created'}, 201


@app.put('/pets/<int:pet_id>')
def update_pet(pet_id):
    return {'message': 'updated'}


@app.delete('/pets/<int:pet_id>')
def delete_pet(pet_id):
    return '', 204
```

!!! tip

    If you want the view function to accepts multiple methods, you still need
    to use `app.route()` decorator. You can mix the use of `app.route()` with the
    shortcuts.

## Using `@input` to validate and deserialize request data

To validate and deserialize a request body or request query parameters, we need to create a
resource schema class first. Think it as a way to describe the valid incoming data. If you
already familiar with Markshmallow, then you already know how to write a resource schema.

Here is a simple input schema for a Pet input resource:

```python
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

!!! tip
    See Schema and Fields chapter (WIP) for the details of how to write a schema and the
    examples for all the fields and validators.

A schema class should inheritate the `apiflask.Schema` class:

```python hl_lines="1 6"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

fields are reprenseted with field classes in `apiflask.fields`:

```python hl_lines="2 7 8"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

To validate a field with specific rule, you can pass a validator or a list of validators
(import them from `apiflask.validators`) to the `validate` argument of field class:

```python hl_lines="3 7 8"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

!!! tip
    Notice we mark the field as required field with `required` arugment. If you want to set
    a default value for a input field when is missing in the input data, you can use
    `missing` argument:

    ```python
    name = String(missing='default name')
    ```

With this schema, we announce the input request body should in the following format:

```json
{
    "name": "the name of the pet",
    "category": "the category of the pet: one of dog and cat"
}
```

Now let's add it to the view funciton which used to create a new pet:

```python hl_lines="1 14"
from apiflask import APIFlask, Schema, input
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


@app.post('/pets')
@input(PetInSchema)
def create_pet(data):
    print(data)
    return {'message': 'created'}, 201
```

You just need to pass the schema class to `@input` decorator. When a request
was received, APIFlask will validate the request body against the schema.

If the validation passed, the data will be inject to the view
function as a positional argument in the form of `dict`. Otherwise,
an error response with the detail of validation result will be returned.

If you want mark the input with deffierent locaiotn, you can pass a `location`
for `@input()` decorator, the value can be:

- Request JSON body: `'json'` (default)
- Upload files: `'files'`
- Form data: `'form'`
- Cookies: `'cookies'`
- HTTP headers: `'headers'`
- Query string: `'query'` (same as `'querystring'`)

!!! warning
    Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

## Using `@output` to formatting response data

Similarly, we can define a schema for output data with `@output` decorator. Here is an example:

```python
from apiflask.fields import String, Integer


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()
```

Since APIFlask will not validate the output data, we only need to list all the field for the output
schema.

!!! tip
    You can set a default value for output field with `default` argument:

    ```python
    name = String(default='default name')
    ```

Now add it to the view function which used to get pet:

```python hl_lines="1 14"
from apiflask import APIFlask, output
from apiflask.fields import String, Integer

app = APIFlask(__name__)


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    return {
        'name': 'Coco',
        'category: 'dog'
    }
```

The default status code for output response is `200`, you can set a different status code
with the `status_code` argument:

```python
@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, status_code=201)
def create_pet(data)
    data['id'] = 2 
    return data
```

Or just:

```python
@output(PetOutSchema, 201)
```

!!! warning
    Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

## Using `@doc` to set up OpenAPI Spec

The `@doc` decorator can be used to set up the OpenAPI Spec for view functions:

```python hl_lines="1 7"
from apiflask import APIFlask, doc

app = APIFlask(__name__)


@app.get('/hello')
@doc(summary='Say hello', description='Some description for the /hello')
def hello():
    return 'Hello'!
```

As default, APIFlask will use the name of the view function as the value of summary.
If your view function named with `get_pet`, then the summary will be "Get Pet".

If the view function has docstring, then the first line of the docstring will be used as summary,
the lines after the empty line of the docstring will be used as description.

!!! note "The precedence of summary setting"
    ```
    @doc(summary='blah') > the first line of docstring > the view function name
    ```

Hence the example above is equals to:

```python hl_lines="6 8"
from apiflask import APIFlask

app = APIFlask(__name__)


@app.get('/hello')
def hello():
    """Say hello

    Some description for the /hello
    """
    return 'Hello'
```

Here are the other arguments for the `@doc` argument:

- `tag`: The tag or tag list of this endpoint, map the tags you passed in the `app.tags`
            attribute. You can pass a list of tag names or just a single tag name string.
            If `app.tags` not set, the blueprint name will be used as tag name.
- `responses`: The other responses for this view function, accepts a dict in a format
    of `{404: 'Not Found'}` or a list of status code (`[404, 418]`).
- `deprecated`: Flag this endpoint as deprecated in API docs. Defaults to `False`.
- `hide`: Hide this endpoint in API docs. Defaults to `False`.

!!! warning
    Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

## Using `@auth_required` to protect your views

You can use `@auth_required` to protect a view with provided authentication settings:

```python hl_lines="1 4 8"
from apiflask import APIFlask, HTTPTokenAuth, auth_required

app = APIFlask(__name__)
auth = HTTPTokenAuth()


@app.get('/')
@auth_required(auth)
def hello():
    return 'Hello'!
```

See [Flask-HTTPAuth's documentation](_flask-httpauth) for more deatils (The chapter 
of authentication support will be added soon).

!!! warning
    Be sure to put it under the routes decorators (i.e. `app.route`, `app.get`,
    `app.post`, etc.).

[_flask-httpauth]: https://flask-httpauth.readthedocs.io/ 

## Using `abort_json()` to return an error response

Similar to Flask's `abort`, but `abort_json` from APIFlask will return a JSON response.

Example:

```python hl_lines="1 8"
from apiflask import APIFlask, abort_json

app = APIFlask(__name__)

@app.get('/<name>')
def hello(name):
    if name == 'Foo':
        abort_json(404, 'This man is missing.')
    return {'hello': name}
```

!!! tip
    When `app.json_errors` is `True` (default), Flask's `abort` will also return
    JSON error response.

You can also raise an `HTTPError` exception to return an error response:

```python hl_lines="1 8"
from apiflask import APIFlask, HTTPError

app = APIFlask(__name__)

@app.get('/<name>')
def hello(name):
    if name == 'Foo':
        rasie HTTPError(404, 'This man is missing.')
    return {'hello': name}
```

The `abort_json()` and `HTTPError` accept the following arugments:

- `status_code`: The status code of the error (4XX and 5xx).
- `message`: The simple description of the error. If not provided,
    the reason phrase of the status code will be used.
- `detail`: The detail information of the error, it can be used to
    provided addition information such as custom error code, documentation
    URL, etc.
- `headers`: A dict of headers used in error response.

## Overview of `apiflask` package

In the end, let's unpack the whole `apiflask` package to check out what it shipped with:

- `APIFlask`: A class used to create an application instance (A wrapper for Flask's `Flask` class).
- `APIBlueprint`: A class used to create a blueprint instance (A wrapper for Flask's `Blueprint` class)..
- `@input`: A docorator used to validate the input/request data from request body, query string, etc.
- `@output`: A docorator used to formatting the response.
- `@auth_required`: A docorator used to protect a view from unauthenticated users.
- `@doc`: A docorator used to set up the OpenAPI spec for view functions.
- `abort_json()`: A function used to abort the request handling process and return an error response. The
    JSON version of Flask's `abort()` function.
- `HTTPError`: An exception used to return error response (used by `abort_json()`).
- `HTTPBasicAuth`: A class used to create an auth instance.
- `HTTPTokenAuth`: A class used to create an auth instance.
- `Schema`: A base class for resource schemas (Will be a wrapper for Marshmallow's `Schema`).
- `fields`: A module contains all the fields (from Marshmallow).
- `validators`: A module contains all the field validators (from Marshmallow).
- `app.get()`: A decorator used to register a route which only accepts *GET* request.
- `app.post()`: A decorator used to register a route which only accepts *POST* request.
- `app.put()`: A decorator used to register a route which only accepts *PUT* request.
- `app.patch()`: A decorator used to register a route which only accepts *PATCH* request.
- `app.delete()`: A decorator used to register a route which only accepts *DELETE* request.

You can learn the details of these APIs in the API reference, or you can continue to read the following
chapters (when I finish them, they will appear on the left navigation :p).
