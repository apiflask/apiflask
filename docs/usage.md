# Basic Usage

This chapter will cover the primary usage of APIFlask.


## Prerequisites

- Python 3.7+
- Flask 1.1+

You also need to know the basic of Flask. Here are some useful free resources
to learn Flask:

- [Flask's Documentation](https://flask.palletsprojects.com/){target=_blank}
- [Official Flask Tutorial](https://flask.palletsprojects.com/tutorial/#tutorial){target=_blank}
- [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world){target=_blank}
- [Flask for Beginners](https://github.com/greyli/flask-tutorial){target=_blank} (Chinese)


## Installation

=== "Linux/macOS"

    ```
    $ pip3 install apiflask
    ```

=== "Windows"

    ```
    > pip install apiflask
    ```

!!! tip "Python dependency management tools"

    The command above use [pip][_pip]{target=_blank} to install APIFlask, you can also use
    other dependencies management tools such as [Poetry][_poetry]{target=_blank},
    [Pipenv][_pipenv]{target=_blank}, [PDM][_pdm]{target=_blank}, etc.

    [_pip]: https://pip.pypa.io/
    [_poetry]: https://python-poetry.org/
    [_pipenv]: https://pipenv.pypa.io/
    [_pdm]: https://pdm.fming.dev/


## Create an `app` instance with `APIFlask` class

Similar to what you did to create a Flask `app` instance, you will need to import
`APIFlask` class from `apiflask` package, then create the `app` instance from
the `APIFlask` class:

```python hl_lines="1 3"
from apiflask import APIFlask

app = APIFlask(__name__)


@app.get('/')
def index():
    return {'message': 'hello'}
```

The default title and version of the API will be `APIFlask` and `0.1.0`; you can 
pass the `title` and the `version` arguments to change these settings:

```python
app = APIFlask(__name__, title='Wonderful API', version='1.0')
```

To run this application, you can save it as `app.py`, then run the `flask run` command:

```bash
$ flask run
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

If your script's name isn't `app.py`, you will need to declare which application
should be started before execute `flask run`. See the note below for more details.

??? note "Assign the specific application to run with `FLASK_APP`"

    In default, Flask will look for an application instance called `app` or `application`
    or application factory function called `create_app` or `make_app` in module/package
    called `app` or `wsgi`. That's why I recommend naming the file as `app.py`. If you
    use a different name, then you need to tell Flask the application module path via the
    environment variable `FLASK_APP`. For example, if your application instance stored in
    a file called `hello.py`, then you will need to set `FLASK_APP` to the module name
    `hello`:

    === "Bash"

        ```
        $ export FLASK_APP=hello
        ```

    === "Windows CMD"

        ```
        > set FLASK_APP=hello
        ```

    === "Powershell"

        ```
        > $env:FLASK_APP="hello"
        ```

    Similarly, If your application instance or application factory function stored in
    `mypkg/__init__.py`, you can set  `FLASK_APP` to the package name:

    === "Bash"

        ```
        $ export FLASK_APP=mypkg
        ```

    === "Windows CMD"

        ```
        > set FLASK_APP=mypkg
        ```

    === "Powershell"

        ```
        > $env:FLASK_APP="mypkg"
        ```

    However, if the application instance or application factory function store in
    `mypkg/myapp.py`, you will need to set  `FLASK_APP` to:

    === "Bash"

        ```
        $ export FLASK_APP=mypkg.myapp
        ```

    === "Windows CMD"

        ```
        > set FLASK_APP=mypkg.myapp
        ```

    === "Powershell"

        ```
        > $env:FLASK_APP="mypkg.myapp"
        ```

    See *[Application Discovery][_app_discovery]{target=_blank}* for more details.

    [_app_discovery]: https://flask.palletsprojects.com/cli/#application-discovery

If you want to make the application restart whenever the code changes, you can enable
reloader with `--reload` option:

```bash
$ flask run --reload
```

!!! tip

    Install `watchdog` for a better performance for the application reloader:

    === "Linux/macOS"

        ```bash
        $ pip3 install watchdog
        ```

    === "Windows"

        ```
        > pip install watchdog
        ```

We highly recommend enabling "debug mode" when developing Flask application. See the
note below for the details.

??? note "Enable the debug mode with `FLASK_ENV`"

    Flask can automatically restart and reload the application when code changes
    and display useful debug information for errors. To enable these features
    in your Flask application, we will need to set the environment variable
    `FLASK_ENV` to `development`:

    === "Bash"

        ```bash
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

    See *[Debug Mode][_debug_mode]{target=_blank}* for more details.

    [_debug_mode]: https://flask.palletsprojects.com/quickstart/#debug-mode


## Manage environment variables with python-dotenv

Manually setting environment is a bit inconvenient since the variable only lives in
the current terminal session. You have to set it every time you reopen the terminal
or reboot the computer. That's why we need to use python-dotenv, and Flask also
has special support for it.

Install `python-dotenv` with pip:

=== "Linux/macOS"

    ```bash
    $ pip3 install python-dotenv
    ```

=== "Windows"

    ```
    > pip install python-dotenv
    ```

Now we can store environment variables in .env files. Flask-related environment
variables should keep in a file called `.flaskenv`:

```ini
# save as .flaskenv
FLASK_APP=hello
FLASK_ENV=development
```

While the secrets values should save in the `.env` file:

```ini
# save as .env
SECRET_KEY=some-random-string
DATABASE_URL=your-database-url
FOO_APP_KEY=some-app-key
```

!!! warning

    Since the `.env` contains sensitive information, do not commit it into the
    Git history. Be sure to ignore it by adding the file name into `.gitignore`.

In the application, now we can read these variables via `os.getenv(key, default_value)`:

```python hl_lines="1 5"
import os

from apiflask import APIFlask

app = APIFlask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
```

Any `flask` command will read environment variables set by `.flaskenv` and `.env`.
Now when you run `flask run`, Flask will read the value of `FLASK_APP` and `FLASK_ENV`
in `.flaskenv` file to find the app instance from given import path and enable the
debug mode:

```bash
$ flask run
 * Environment: development
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 101-750-099
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

See *[Environment Variables From dotenv][_dotenv]{target=_blank}* for more details.

[_dotenv]: https://flask.palletsprojects.com/en/1.1.x/cli/#environment-variables-from-dotenv


## Interactive API documentation

Once you have created the app instance, the interactive API documentation will be
available at <http://localhost:5000/docs> and <http://localhost:5000/redoc>. On
top of that, the OpenAPI spec file will be available at
<http://localhost:5000/openapi.json>.

You can refresh the documentation whenever you added a new route or added the input
and output definition for the view function in the following sections.


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

However, with APIFlask, instead of setting `methods` argument for each route, you can
also use the following shortcuts decorators:

- `app.get()`: register a route that only accepts *GET* request.
- `app.post()`: register a route that only accepts *POST* request.
- `app.put()`: register a route that only accepts *PUT* request.
- `app.patch()`: register a route that only accepts *PATCH* request.
- `app.delete()`: register a route that only accepts *DELETE* request.

Here is the same example with the route shortcuts:

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

!!! note "Handling multiple HTTP methods in one view function"

    You can't pass the `methods` argument to route shortcuts. If you want the
    view function to accept multiple HTTP methods, you will need to use the
    `app.route()` decorator to pass the `methods` argument:

    ```python
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return {'message': 'hello'}
    ```

    Or you can do something like this:

    ```python
    @app.get('/')
    @app.post('/')
    def index():
        return {'message': 'hello'}
    ```

    By the way, you can mix the use of `app.route()` with the shortcuts in your
    application.


## Use `@input` to validate and deserialize request data

To validate and deserialize a request body or request query parameters, we need to
create a resource schema class first. Think of it as a way to describe the valid
incoming data. If you already familiar with Marshmallow, then you already know
how to write a resource schema.

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

    See Schema and Fields chapter (WIP) for the details of how to write a schema and
    the examples for all the fields and validators.

A schema class should inherit the `apiflask.Schema` class:

```python hl_lines="1 6"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

fields are represented with field classes in `apiflask.fields`:

```python hl_lines="2 7 8"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

To validate a field with a specific rule, you can pass a validator or a list of
validators (import them from `apiflask.validators`) to the `validate` argument
of the field class:

```python hl_lines="3 7 8"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

!!! tip

    Notice we mark the field as a required field with the `required` parameter.
    If you want to set a default value for an input field when is missing in
    the input data, you can use the `missing` parameter:

    ```python
    name = String(missing='default name')
    ```

With this schema, we declare that the input request body should appear in the
following format:

```json
{
    "name": "the name of the pet",
    "category": "the category of the pet: one of dog and cat"
}
```

Now let's add it to the view function which used to create a new pet:

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

You just need to pass the schema class to the `@input` decorator. When a request
was received, APIFlask will validate the request body against the schema.

If the validation passed, the data will inject into the view function as
a positional argument in the form of `dict`. Otherwise, an error response
with the detail of the validation result will be returned.

In the example above, I use the name `data` to accept the input data dict.
You can change the argument name to whatever you like. Since this is a dict,
you can do something like this to create an ORM model instance:

```python hl_lines="5"
@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema)
def create_pet(pet_id, data):
    pet = Pet(**data)
    return pet
```

or update an ORM model class instance like this:

```python hl_lines="6 7"
@app.patch('/pets/<int:pet_id>')
@input(PetInSchema)
@output(PetOutSchema)
def update_pet(pet_id, data):
    pet = Pet.query.get(pet_id)
    for attr, value in data.items():
        setattr(pet, attr, value)
    return pet
```

If you want to mark the input with a different location, you can pass a `location`
argument for `@input()` decorator, the value can be:

- Request JSON body: `'json'` (default)
- Upload files: `'files'`
- Form data: `'form'`
- Cookies: `'cookies'`
- HTTP headers: `'headers'`
- Query string: `'query'` (same as `'querystring'`)

!!! warning

    Be sure to put the `@input` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


## Use `@output` to formatting response data

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

Now add it to the view function which used to get a pet resource:

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

The default status code for output response is `200`, you can set a different
status code with the `status_code` argument:

```python hl_lines="3"
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

If you want to return a 204 response, you can use the `EmptySchema` from `apiflask.schemas`:

```python hl_lines="1 5"
from apiflask.schemas import EmptySchema


@app.delete('/pets/<int:pet_id>')
@output(EmptySchema, 204)
def delete_pet(pet_id):
    return ''
```

From version 0.4.0, you can use a empty dict to represent empty schema:

```python hl_lines="2"
@app.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    return ''
```

!!! warning "The `@output` decorator can only use once"

    You can only define one main success response for your view function,
    which means you can only use one `@output` decorator. If you want to
    add more alternative responses for a view in the OpenAPI spec, you can
    use the `@doc` decorator and pass a list to the `responses` parameter.
    For example:
    
    ```python hl_lines="4"
    @app.put('/pets/<int:pet_id>')
    @input(PetInSchema)
    @output(PetOutSchema)  # 200
    @doc(responses=[204, 404])
    def update_pet(pet_id, data):
        pass
    ```

!!! warning

    Be sure to put the `@output` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


## The return value of the view function

When you are using a `@output(schema)` decorator, you should return a dict or object
that matches the schema you passed. For example, here is your schema:

```python
from apiflask import Schema
from apiflask.fields import String, Integer


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()
```

Now you can return a dict:

```python
@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    return {
        'id': 1,
        'name': 'Coco',
        'category: 'dog'
    }
```

or you can return an ORM model instance directly:

```python hl_lines="5"
@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    pet = Pet.query.get(pet_id)
    return pet
```

Notice your ORM model class should have the fields defined in the schema class:

```python
class Pet(Model):
    id = Integer()
    name = String()
    category = String()
```

!!! tip "What if I want to use a different field name in the schema?"

    For example, in your ORM model class, you have a `phone` field that
    store the user's phone number:

    ```python
    class User(Model):
        phone = String()
    ```

    Now you want to output the field with the name `phone_number`, then you
    can use `data_key` argument to declare the actual key name to load from:

    ```python
    class UserOutSchema(Schema):
        phone_number = String(data_key='phone')
    ```

The default status code is `200`, if you want to use a different status code,
you can pass a `status_code` argument in the `@output` decorator:

```python hl_lines="3"
@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data)
    # ...
    return pet
```

You don't need to return the same status code in the end of the view function
(i.e., `return data, 201`):

```python hl_lines="8"
@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data)
    # ...
    # equals to:
    # return pet, 201
    return pet
```

When you want to pass a header dict, you can pass the dict as the second element
of the return tuple:

```python hl_lines="8"
@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data)
    # ...
    # equals to:
    # return pet, 201, {'FOO': 'bar'}
    return pet, {'FOO': 'bar'}
```

!!! tips

    Be sure to always set the `status_code` argument in `@output` when you want
    to use a non-200 status code. If there is a mismatch, the `status_code`
    passed in `@output` will be used in OpenAPI spec, while the actual response
    will use the status code you returned at the end of the view function.


## Use `@doc` to set up OpenAPI Spec

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
If your view function is named with `get_pet`, then the summary will be "Get Pet".

If the view function has docstring, then the first line of the docstring will be used
as the summary, the lines after the empty line of the docstring will be used as
the description.

!!! note "The precedence of summary setting"

    ```
    @doc(summary='blah') > the first line of docstring > the view function name
    ```

Hence the example above is equals to:

```python hl_lines="8 10"
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
            If `app.tags` is not set, the blueprint name will be used as the tag name.
- `responses`: The other responses for this view function, accepts a dict in a format
    of `{404: 'Not Found'}` or a list of status code (`[404, 418]`).
- `deprecated`: Flag this endpoint as deprecated in API docs. Defaults to `False`.
- `hide`: Hide this endpoint in API docs. Defaults to `False`.

!!! warning

    Be sure to put the `@doc` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


## Use `@auth_required` to protect your views

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

See [Flask-HTTPAuth's documentation][_flask-httpauth]{target=_blank} for more
details (The chapter of authentication support will be added soon).

!!! warning

    Be sure to put the `@auth_required` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).

[_flask-httpauth]: https://flask-httpauth.readthedocs.io/


## Use class-based views

!!! warning "Version >= 0.5.0"

    This feature was added in the [version 0.5.0](/changelog/#version-050).

You can create a group of routes under the same URL rule with the `MethodView` class.
Here is a simple example:

```python
from flask.views import MethodView
from apiflask import APIFlask

app = APIFlask(__name__)


@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):

    def get(self, pet_id):
        return {'message': 'OK'}

    def delete(self, pet_id):
        return '', 204
```

When creating a view class, it needs to inherit from the `MethodView` class:

```python hl_lines="1 4"
from flask.views import MethodView

@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):
    # ...
```

The class should be decorated with the `route` decorator:

```python hl_lines="1"
@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):
    # ...
```

!!! tips

    If the `endpoint` argument isn't provided, the class name will be used as
    endpoint. You don't need to pass a `methods` argument, since Flask will handle
    it for you.

!!! warning

    You should use `app.route` to register a view class instead of using
    `app.add_url_rule` method.

Now, you can define view methods for each HTTP method, use the (HTTP) method name as method name:

```python hl_lines="4 7 10 13 16"
@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):

    def get(self, pet_id):  # triggered by GET request
        return {'message': 'OK'}

    def post(self, pet_id):  # triggered by POST request
        return {'message': 'OK'}

    def put(self, pet_id):  # triggered by PUT request
        return {'message': 'OK'}

    def delete(self, pet_id):  # triggered by DELETE request
        return '', 204

    def patch(self, pet_id):  # triggered by PATCH request
        return {'message': 'OK'}
```

With the example application above, when the user sends a *GET* request to
`/pets/<int:pet_id>`, the `get()` method of the `Pet` class will be called,
and so on for the others.

When you use decorators like `@input`, `@output`, be sure to use it on method
instead of class:

```python hl_lines="4 5 9 10 11 15 16"
@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):

    @output(PetOutSchema)
    @doc(summary='Get a Pet')
    def get(self, pet_id):
        # ...

    @auth_required(auth)
    @input(PetInSchema)
    @output(PetOutSchema)
    def put(self, pet_id, data):
        # ...

    @input(PetInSchema(partial=True))
    @output(PetOutSchema)
    def patch(self, pet_id, data):
        # ...
```

If you want to apply a decorator for all methods, instead of repeat yourself,
you can pass the decorator to the class attribute `decorators`, it accepts
a list of decorators:

```python hl_lines="4"
@app.route('/pets/<int:pet_id>', endpoint='pet')
class Pet(MethodView):

    decorators = [auth_required(auth), doc(responses=[404])]

    @output(PetOutSchema)
    @doc(summary='Get a Pet')
    def get(self, pet_id):
        # ...

    @auth_required(auth)
    @input(PetInSchema)
    @output(PetOutSchema)
    def put(self, pet_id, data):
        # ...

    @input(PetInSchema(partial=True))
    @output(PetOutSchema)
    def patch(self, pet_id, data):
        # ...
```


## Use `abort()` to return an error response

Similar to Flask's `abort`, but `abort` from APIFlask will return a JSON response.

Example:

```python hl_lines="1 8"
from apiflask import APIFlask, abort

app = APIFlask(__name__)

@app.get('/<name>')
def hello(name):
    if name == 'Foo':
        abort(404, 'This man is missing.')
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

The `abort()` and `HTTPError` accept the following arguments:

- `status_code`: The status code of the error (4XX and 5xx).
- `message`: The simple description of the error. If not provided,
    the reason phrase of the status code will be used.
- `detail`: The detailed information of the error, it can be used to
    provide additional information such as custom error code, documentation
    URL, etc.
- `headers`: A dict of headers used in the error response.

!!! warning

    The function `abort_json()` was renamed to `abort()` in
    the [version 0.4.0](/changelog/#version-040).


## Overview of the `apiflask` package

In the end, let's unpack the whole `apiflask` package to check out what it shipped with:

- `APIFlask`: A class used to create an application instance (A wrapper for Flask's `Flask` class).
- `APIBlueprint`: A class used to create a blueprint instance (A wrapper for Flask's `Blueprint` class)..
- `@input`: A decorator used to validate the input/request data from request body, query string, etc.
- `@output`: A decorator used to format the response.
- `@auth_required`: A decorator used to protect a view from unauthenticated users.
- `@doc`: A decorator used to set up the OpenAPI spec for view functions.
- `abort()`: A function used to abort the request handling process and return an error response. The JSON version of Flask's `flask.abort()` function.
- `HTTPError`: An exception used to return error response (used by `abort()`).
- `HTTPBasicAuth`: A class used to create an auth instance.
- `HTTPTokenAuth`: A class used to create an auth instance.
- `Schema`: A base class for resource schemas (Will be a wrapper for Marshmallow's `Schema`).
- `fields`: A module contains all the fields (from Marshmallow).
- `validators`: A module contains all the field validators (from Marshmallow).
- `app.get()`: A decorator used to register a route that only accepts *GET* request.
- `app.post()`: A decorator used to register a route that only accepts *POST* request.
- `app.put()`: A decorator used to register a route that only accepts *PUT* request.
- `app.patch()`: A decorator used to register a route that only accepts *PATCH* request.
- `app.delete()`: A decorator used to register a route that only accepts *DELETE* request.
- `app.route()`: A decorator used to register a route. It accepts a `methods`
parameter to specify a list of accepted methods, default to *GET* only. It can also
be used on the `MethodView`-based view class.

You can learn the details of these APIs in the [API reference](/api/app), or you can
continue to read the following chapters.
