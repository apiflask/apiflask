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

??? note "Assign the specific application to run"

    In default, Flask will look for an application instance called `app` or `application`
    or application factory function called `create_app` or `make_app` in module/package
    called `app` or `wsgi`. That's why I recommend naming the file as `app.py`. If you
    use a different name, then you need to tell Flask the application module path via the
    `--app` (Flask 2.2+) option or the environment variable `FLASK_APP`. For example, if
    your application instance stored in a file called `hello.py`, then you will need to
    set `--app` or `FLASK_APP` to the module name `hello`:

    ```
    $ flask --app hello run
    ```

    or:

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
    `mypkg/__init__.py`, you can pass the package name:

    ```
    $ flask --app mypkg run
    ```

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
    `mypkg/myapp.py`, you will need to use:

    ```
    $ flask --app mypkg.myapp run
    ```

    or:

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

??? note "Enable the debug mode"

    Flask can automatically restart and reload the application when code changes
    and display useful debug information for errors. To enable these features
    in your Flask application, we will need to use the `--debug` option:

    ```
    $ flask --debug run
    ```

    If you are not using the latest Flask version (>2.2), you will need to set
    the environment variable `FLASK_DEBUG` to `True` instead:

    === "Bash"

        ```bash
        $ export FLASK_DEBUG=True
        ```

    === "Windows CMD"

        ```
        > set FLASK_DEBUG=True
        ```

    === "Powershell"

        ```
        > $env:FLASK_DEBUG="True"
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
available at <http://localhost:5000/docs>. On
top of that, the OpenAPI spec file is available at <http://localhost:5000/openapi.json>.

If you want to preview the spec or save the spec to a local file, use [the `flask spec`
command](/openapi/#the-flask-spec-command).

You can refresh the documentation whenever you added a new route or added the input
and output definition for the view function in the following sections.

Read the *[API Documentations](/api-docs)* chapter for the advanced topics on API docs.


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


## Move to new API decorators

From APIFlask 0.12, the four standalone API decorators (i.e. `@input`, `@output`,
`@doc`, and `@auth_required`) were moved to `APIFlask` and `APIBlueprint` classes.
Now access them with your application or blueprint instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

@app.get('/')
@app.input(Foo)
@app.output(Bar)
def hello():
    return {'message': 'Hello'}
```

instead of:

```python
from apiflask import APIFlask, input, output

app = APIFlask(__name__)

@app.get('/')
@input(Foo)
@output(Bar)
def hello():
    return {'message': 'Hello'}
```

The old standalone decorators were deprecated since 0.12, and will be removed in the
1.0 version. Notice all the usage in the docs are updated, you may want to
[upgrade APIFlask](/changelog/) to update the usage.


## Use `@app.input` to validate and deserialize request data

To validate and deserialize a request body or request query parameters, we need to
create a data schema class first. Think of it as a way to describe the valid
incoming data. If you already familiar with marshmallow, then you already know
how to write a data schema.

Here is a simple input schema for a Pet input resource:

```python
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetIn(Schema):
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


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

fields are represented with field classes in `apiflask.fields`:

```python hl_lines="2 7 8"
from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf


class PetIn(Schema):
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


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))
```

!!! tip

    Notice we mark the field as a required field with the `required` parameter.
    If you want to set a default value for an input field when is missing in
    the input data, you can use the `load_default` parameter:

    ```python
    name = String(load_default='default name')
    ```

With this schema, we declare that the input request body should appear in the
following format:

```json
{
    "name": "the name of the pet",
    "category": "the category of the pet: one of dog and cat"
}
```
!!! notes

    Read the *[Data Schema](/schema)* chapter for the advanced topics on data schema.

Now let's add it to the view function which is used to create a new pet:

```python hl_lines="1 14"
from apiflask import APIFlask, Schema, input
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


@app.post('/pets')
@app.input(PetIn)
def create_pet(data):
    print(data)
    return {'message': 'created'}, 201
```

You just need to pass the schema class to the `@app.input` decorator. When a request
was received, APIFlask will validate the request body against the schema.

If the validation passed, the data will inject into the view function as
a positional argument in the form of `dict`. Otherwise, an error response
with the detail of the validation result will be returned.

In the example above, I use the name `data` to accept the input data dict.
You can change the argument name to whatever you like. Since this is a dict,
you can do something like this to create an ORM model instance:

```python hl_lines="5"
@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut)
def create_pet(pet_id, data):
    pet = Pet(**data)
    return pet
```

or update an ORM model class instance like this:

```python hl_lines="6 7"
@app.patch('/pets/<int:pet_id>')
@app.input(PetIn)
@app.output(PetOut)
def update_pet(pet_id, data):
    pet = Pet.query.get(pet_id)
    for attr, value in data.items():
        setattr(pet, attr, value)
    return pet
```

If you want to mark the input with a different location, you can pass a `location`
argument for `@app.input()` decorator, the value can be:

- Request JSON body: `'json'` (default)
- Upload files: `'files'`
- Form data: `'form'`
- Form data and files: `'form_and_files'`
- Cookies: `'cookies'`
- HTTP headers: `'headers'`
- Query string: `'query'` (same as `'querystring'`)
- Path variable (URL variable): `'path'` (same as `'view_args'`, added in APIFlask 1.0.2)

!!! warning

    Be sure to put the `@app.input` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


Read the *[Request Handling](/request)* chapter for the advanced topics on request handling.


## Use `@app.output` to format response data

Similarly, we can define a schema for output data with `@app.output` decorator. Here is an example:

```python
from apiflask.fields import String, Integer


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()
```

Since APIFlask will not validate the output data, we only need to list all the field for the output
schema.

!!! tip

    You can set a default value for output field with the `dump_default` argument:

    ```python
    name = String(dump_default='default name')
    ```

Now add it to the view function which used to get a pet resource:

```python hl_lines="1 14"
from apiflask import APIFlask, output
from apiflask.fields import String, Integer

app = APIFlask(__name__)


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    return {
        'name': 'Coco',
        'category': 'dog'
    }
```

The default status code for output response is `200`, you can set a different
status code with the `status_code` argument:

```python hl_lines="3"
@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut, status_code=201)
def create_pet(data):
    data['id'] = 2
    return data
```

Or just:

```python
@app.output(PetOut, status_code=201)
```

If you want to return a 204 response, you can use the `EmptySchema` from `apiflask.schemas`:

```python hl_lines="1 5"
from apiflask.schemas import EmptySchema


@app.delete('/pets/<int:pet_id>')
@app.output(EmptySchema, status_code=204)
def delete_pet(pet_id):
    return ''
```

From version 0.4.0, you can use an empty dict to represent empty schema:

```python hl_lines="2"
@app.delete('/pets/<int:pet_id>')
@app.output({}, status_code=204)
def delete_pet(pet_id):
    return ''
```

!!! warning "The `@app.output` decorator can only use once"

    You can only define one main success response for your view function,
    which means you can only use one `@app.output` decorator. If you want to
    add more alternative responses for a view in the OpenAPI spec, you can
    use the `@app.doc` decorator and pass a list to the `responses` parameter.
    For example:

    ```python hl_lines="4"
    @app.put('/pets/<int:pet_id>')
    @app.input(PetIn)
    @app.output(PetOut)  # 200
    @app.doc(responses=[204, 404])
    def update_pet(pet_id, data):
        pass
    ```

!!! warning

    Be sure to put the `@app.output` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


Read the *[Response Formatting](/response)* chapter for the advanced topics on request formatting.


## The return value of the view function

When you are using a `@app.output(schema)` decorator, you should return a dict or object
that matches the schema you passed. For example, here is your schema:

```python
from apiflask import Schema
from apiflask.fields import String, Integer


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()
```

Now you can return a dict:

```python
@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    return {
        'id': 1,
        'name': 'Coco',
        'category': 'dog'
    }
```

or you can return an ORM model instance directly:

```python hl_lines="5"
@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
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

!!! tip "What if I want to use a different external field name?"

    For example, in your ORM model class, you have a `phone` field that
    store the user's phone number:

    ```python
    class User(Model):
        phone = String()
    ```

    Now you want to output the field with the name `phone_number`, then you can use
    `data_key` to declare the actual key name to dump to:

    ```python
    class UserOut(Schema):
        phone = String(data_key='phone_number')
    ```

    This schema will generate something like `{'phone_number': ...}`.

    Similarly, you can tell APIFlask to load from different key in input schema:

    ```python
    class UserIn(Schema):
        phone = String(data_key='phone_number')
    ```

    This schema expects the user input is something like `{'phone_number': ...}`.

The default status code is `200`, if you want to use a different status code,
you can pass a `status_code` argument in the `@app.output` decorator:

```python hl_lines="3"
@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut, status_code=201)
def create_pet(data):
    # ...
    return pet
```

You don't need to return the same status code in the end of the view function
(i.e., `return data, 201`):

```python hl_lines="8"
@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut, status_code=201)
def create_pet(data):
    # ...
    # equals to:
    # return pet, 201
    return pet
```

When you want to pass a header dict, you can pass the dict as the second element
of the return tuple:

```python hl_lines="8"
@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut, status_code=201)
def create_pet(data):
    # ...
    # equals to:
    # return pet, 201, {'FOO': 'bar'}
    return pet, {'FOO': 'bar'}
```

!!! tip

    Be sure to always set the `status_code` argument in `@app.output` when you want
    to use a non-200 status code. If there is a mismatch, the `status_code`
    passed in `@app.output` will be used in OpenAPI spec, while the actual response
    will use the status code you returned at the end of the view function.


## The OpenAPI generating support and the `@app.doc` decorator

APIFlask provides automatic OpenAPI spec generating support, while also allows
you to customize the spec:

- Most of the fields of the `info` object and top-level field of `OpenAPI`
objct are accessible with configuration variables.
- The `tag` object, Operation `summary` and `description` will generated from
the blueprint name, the view function name and docstring.
- You can register a spec processor function to process the spec.
- `requestBody` and `responses` fields can be set with the `input` and `output`
decorator.
- Other operation fields can be set with the `doc` decorator:

```python hl_lines="1 7"
from apiflask import APIFlask, doc

app = APIFlask(__name__)


@app.get('/hello')
@app.doc(summary='Say hello', description='Some description for the /hello')
def hello():
    return 'Hello'
```

See *[Use the `doc` decorator](/openapi/#use-the-doc-decorator)* for more details
about OpenAPI genenrating and the usage of the `doc` decorator.

!!! warning

    Be sure to put the `@app.doc` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).


## Use `@app.auth_required` to protect your views

Based on [Flask-HTTPAuth](https://github.com/miguelgrinberg/Flask-HTTPAuth), APIFlask
provides three types of authentication:

### HTTP Basic

To implement an HTTP Basic authentication, you will need to:

- Create an `auth` object with `HTTPBasicAuth`
- Register a callback function with `@auth.verify_password`, the function
  should accept `username` and `password`, return the corresponding user object
  or `None`.
- Protect the view function with `@app.auth_required(auth)`.
- Access the current user object in your view function with `auth.current_user`.

```python
from apiflask import APIFlask, HTTPBasicAuth

app = APIFlask(__name__)
auth = HTTPBasicAuth()  # create the auth object


@auth.verify_password
def verify_password(username, password):
    # get the user from the database, check the password
    # then return the user if the password matches
    # ...

@app.route('/')
@app.auth_required(auth)
def hello():
    return f'Hello, {auth.current_user}!'
```

### HTTP Bearer

To implement an HTTP Bearer authentication, you will need to:

- Create an `auth` object with `HTTPTokenAuth`
- Register a callback function with `@auth.verify_password`, the function
  should accept `token`, return the corresponding user object or `None`.
- Protect the view function with `@app.auth_required(auth)`.
- Access the current user object in your view function with `auth.current_user`.

```python
from apiflask import APIFlask, HTTPTokenAuth

app = APIFlask(__name__)
auth = HTTPTokenAuth()  # create the auth object
# or HTTPTokenAuth(scheme='Bearer')


@auth.verify_token  # register a callback to verify the token
def verify_token(token):
    # verify the token and get the user id
    # then query and return the corresponding user from the database
    # ...

@app.get('/')
@app.auth_required(auth)  # protect the view
def hello():
    # access the current user with auth.current_user
    return f'Hello, {auth.current_user}'!
```

### API Keys (in header)

Similar to the Bearer type, but set the `scheme` to `ApiKey` when creating the
auth object:

```python
from apiflask import HTTPTokenAuth

HTTPTokenAuth(scheme='ApiKey')
```

or with a custom header:

```python
from apiflask import HTTPTokenAuth

HTTPTokenAuth(scheme='ApiKey', header='X-API-Key')

# ...
```

You can set the OpenAPI security description with the `description` parameter
in `HTTPBasicAuth` and `HTTPTokenAuth`.

See [Flask-HTTPAuth's documentation][_flask-httpauth]{target=_blank} to learn
the details. However, remember to
import `HTTPBasicAuth` and `HTTPTokenAuth` from APIFlask and use `@app.auth_required`
instead of `@auth.login_required` for your view functions.

!!! warning

    Be sure to put the `@app.auth_required` decorator under the routes decorators
    (i.e., `app.route`, `app.get`, `app.post`, etc.).

[_flask-httpauth]: https://flask-httpauth.readthedocs.io/

Read the *[Authentication](/authentication)* chapter for the advanced topics on authentication.


## Use class-based views

!!! warning "Version >= 0.5.0"

    This feature was added in the [version 0.5.0](/changelog/#version-050).

You can create a group of routes under the same URL rule with the `MethodView` class.
Here is a simple example:

```python
from apiflask import APIFlask
from apiflask.views import MethodView

app = APIFlask(__name__)


class Pet(MethodView):

    def get(self, pet_id):
        return {'message': 'OK'}

    def delete(self, pet_id):
        return '', 204


app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
```

When creating a view class, it needs to inherit from the `MethodView` class, since APIFlask
can only generate OpenAPI spec for `MethodView`-based view classes.

Now, you can define view methods for each HTTP method, use the (HTTP) method name as method name:

```python
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


app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
```

With the example application above, when the user sends a *GET* request to
`/pets/<int:pet_id>`, the `get()` method of the `Pet` class will be called,
and so on for the others.

Normally you don't need to specify the methods, unless you want to register
multiple rules for one single view classe. For example, register the `post` method
to a different URL rule than the others:

```python
class Pet(MethodView):
    # ...

pet_view = Pet.as_view('pet')
app.add_url_rule('/pets/<int:pet_id>', view_func=pet_view, methods=['GET', 'PUT', 'DELETE', 'PATCH'])
app.add_url_rule('/pets', view_func=pet_view, methods=['POST'])
```

However, you may want to create separate classes for different URL rules.

When you use decorators like `@app.input`, `@app.output`, be sure to use it on method
instead of class:

```python
class Pet(MethodView):

    @app.output(PetOut)
    @app.doc(summary='Get a Pet')
    def get(self, pet_id):
        # ...

    @app.auth_required(auth)
    @app.input(PetIn)
    @app.output(PetOut)
    def put(self, pet_id, data):
        # ...

    @app.input(PetIn(partial=True))
    @app.output(PetOut)
    def patch(self, pet_id, data):
        # ...


app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
```

If you want to apply a decorator for all methods, instead of repeat yourself,
you can pass the decorator to the class attribute `decorators`, it accepts
a list of decorators:

```python hl_lines="3"
class Pet(MethodView):

    decorators = [auth_required(auth), doc(responses=[404])]

    @app.output(PetOut)
    @app.doc(summary='Get a Pet')
    def get(self, pet_id):
        # ...

    @app.auth_required(auth)
    @app.input(PetIn)
    @app.output(PetOut)
    def put(self, pet_id, data):
        # ...

    @app.input(PetIn(partial=True))
    @app.output(PetOut)
    def patch(self, pet_id, data):
        # ...


app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
```

Read [Flask docs on class-based views](https://flask.palletsprojects.com/views/) for more information.


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
        raise HTTPError(404, 'This man is missing.')
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
- `@app.input()`: A decorator used to validate the input/request data from request body, query string, etc.
- `@app.output()`: A decorator used to format the response.
- `@app.auth_required()`: A decorator used to protect a view from unauthenticated users.
- `@app.doc()`: A decorator used to set up the OpenAPI spec for view functions.
- `abort()`: A function used to abort the request handling process and return an error response. The JSON version of Flask's `flask.abort()` function.
- `HTTPError`: An exception used to return error response (used by `abort()`).
- `HTTPBasicAuth`: A class used to create an auth instance.
- `HTTPTokenAuth`: A class used to create an auth instance.
- `Schema`: A base class for resource schemas (Will be a wrapper for marshmallow's `Schema`).
- `fields`: A module contains all the fields (from marshmallow).
- `validators`: A module contains all the field validators (from marshmallow).
- `app.get()`: A decorator used to register a route that only accepts *GET* request.
- `app.post()`: A decorator used to register a route that only accepts *POST* request.
- `app.put()`: A decorator used to register a route that only accepts *PUT* request.
- `app.patch()`: A decorator used to register a route that only accepts *PATCH* request.
- `app.delete()`: A decorator used to register a route that only accepts *DELETE* request.
- `app.route()`: A decorator used to register a route. It accepts a `methods`
parameter to specify a list of accepted methods, default to *GET* only. It can also
be used on the `MethodView`-based view class.
- `$ flask spec`: A command to output the spec to stdout or a file.

You can learn the details of these APIs in the [API reference](/api/app), or you can
continue to read the following chapters.
