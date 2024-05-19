# Migrating from Flask-RESTPlus or Flask-RESTX

Flask-RESTPlus is an extension for Flask that adds support for quickly building REST APIs. It is no longer maintained and has been superseded by Flask-RESTX.

APIFlask and Flask-RESTPlus/Flask-RESTx share similar goals and features, but the implementation is different. This guide will help you migrate from Flask-RESTPlus/Flask-RESTX to APIFlask.


## Initialization

=== "Flask-RESTPlus"


    ```python
    from flask import Flask
    from flask_restx import Api

    app = Flask(__name__)
    api = Api(app)
    ```

    Or:

    ```python
    from flask import Flask
    from flask_restx import Api

    api = Api()

    app = Flask(__name__)
    api.init_app(app)
    ```

=== "APIFlask"


    ```python
    from apiflask import APIFlask

    app = APIFlask(__name__)
    ```


## Routing

=== "Flask-RESTPlus"

    ```python
    from flask import Flask
    from flask_restx import Resource, Api

    app = Flask(__name__)
    api = Api(app)


    @api.route('/hello')
    class HelloWorld(Resource):
        def get(self):
            return {'message': 'Hello world'}
    ```

=== "APIFlask"

    ```python
    from apiflask import APIFlask

    app = APIFlask(__name__)


    @app.get('/hello')
    def hello_world():
        return {'message': 'Hello world!'}
    ```

    or:

    ```python
    from apiflask import APIFlask
    from flask.views import MethodView

    app = APIFlask(__name__)


    class HelloWorld(MethodView):
        def get(self):
            return {'message': 'Hello world!'}

    app.add_url_rule('/hello', view_func=Hello.as_view('hello'))
    ```

## Response Formatting/Marshalling

=== "Flask-RESTPlus"

    Flask-RESTPlus uses the `api.model` to create a model and uses `marshal_with` decorator for response formatting.

    ```python
    from flask_restplus import fields, marshal_with

    user_fields = api.model('User', {
        'name': fields.String,
        'age': fields.Integer
    })

    @api.route('/users')
    class User(Resource):
        @marshal_with(user_fields)
        def get(self):
            return {'name': 'John', 'age': 30}
    ```

=== "APIFlask"

    APIFlask uses [marshmallow](https://marshmallow.readthedocs.io/en/stable/) to define data schema and uses `app.output` for response formatting.

    ```python
    from apiflask import Schema
    from apiflask.fields import Integer, String

    class User(Schema):
        name = String()
        age = Integer()

    @app.get('/users')
    @app.output(User)
    def get_user():
        return {'name': 'John', 'age': 30}
    ```

    You can also import the `Schema`, `Integer`, and `String` from `marshmallow` directly.


## Request Parsing / Argument Parsing

=== "Flask-RESTPlus"

    Flask-RESTPlus uses the built-in `reqparse` module for request parsing.

    ```python
    from flask_restplus import reqparse

    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)
    parser.add_argument('age', type=int, required=True)
    args = parser.parse_args()
    ```

    But the `reqparse` module is deprecated and will be removed in the future version.

    Besides, you can also use `api.expect` with API model for request parsing.

    ```python
    from flask_restplus import fields, marshal_with

    user_fields = api.model('User', {
        'name': fields.String,
        'age': fields.Integer
    })

    @api.route('/users')
    class User(Resource):
        @api.expect(user_fields)
        def post(self):
            pass
    ```

=== "APIFlask"

    APIFlask uses [marshmallow](https://marshmallow.readthedocs.io/en/stable/) to define data schema and uses `api.input` for request parsing.

    ```python
    from apiflask import Schema
    from apiflask.fields import Integer, String

    class User(Schema):
        name = String(required=True)
        age = Integer(required=True)

    @app.get('/')
    @app.input(User, location='json')
    def create_user(json_data):  # the arg name defaults to the `<location_name>_data`
        pass
    ```

    You can also import the `Schema`, `Integer`, and `String` from `marshmallow` directly.


## Error Handling

=== "Flask-RESTPlus"

    Flask-RESTPlus automatically handles errors and returns a JSON response with the error message.

    ```json
    {
        "message": "The browser (or proxy) sent a request that this server could not understand."
    }
    ```

    To add custom error data, you can add `data` attribute to the exception or use the `flask_restplus.abort` method.

    ```python
    from flask_restplus import abort
    abort(400, custom='value')
    ```

    output:

    ```json
    {
        "message": "The browser (or proxy) sent a request that this server could not understand.",
        "custom": "value"
    }
    ```

    To document the error response, you can use the `:raises` annotation in the docstring.

    ```python
    @api.route('/test/')
    class TestResource(Resource):
        def get(self):
            '''
            Do something

            :raises CustomException: In case of something
            '''
            pass
    ```

=== "APIFlask"

    APIFlask also automatically handles errors and returns a JSON response with the error message.

    ```json
    {
        "message": "The browser (or proxy) sent a request that this server could not understand.",
        "detail": {}
    }
    ```

    To add custom fields, define a custom exception class that inherits from `HTTPException`:

    ```python
    from apiflask import HTTPError

    class PetNotFound(HTTPError):
        status_code = 404
        message = 'This pet is missing.'
        extra_data = {
            'error_code': '2323',
            'error_docs': 'https://example.com/docs/missing'
        }
    ```

    or use `apiflask.abort` with `extra_data` argument:

    ```python
    abort(
        400,
        message='Something is wrong...',
        extra_data={
            'docs': 'http://example.com',
            'error_code': 1234
        }
    )
    ```

    output:

    ```json
    {
        "message": "Something is wrong...",
        "detail": {},
        "docs": "http://example.com",
        "error_code": 1234
    }
    ```

    To document the error response, you can use the `app.doc` decorator:

    ```python
    @app.get('/')
    @app.doc(responses=[400])
    def hello():
        return 'Hello'
    ```


## OpenAPI (f.k.a Swagger) Documentation

For Flask-RESTPlus/Flask-RESTX, the default OpenAPI spec is available at `/swagger.json`, and the Swagger UI is available at the API root `/`.

For APIFlask, the default OpenAPI spec is available at `/openapi.json`, and the Swagger UI or other alternative UIs is available at `/docs`.

To collect the API documentation, they provide similar APIs, see the following table for the details:

| Flask-RESTPlus/Flask-RESTX | APIFlask |
| --- | --- |
| `@api.doc()` | `@app.doc()` |
| `@api.marshal_with()` | `@app.output()` |
| `@api.expect()` | `@app.input()` |
| `@api.responses()` | `@app.doc(responses=...)` |
| `@api.deprecated` | `@app.doc(deprecated=True)` |
| `@api.hide` | `@app.doc(hide=True)` |

They also use the similar way to define the basic settings of the API documentation:

Flask-RESTPlus/Flask-RESTX:

```python
from flask import Flask
from flask_restplus import Api

app = Flask(__name__)
api = Api(app, version='1.0', title='Sample API', description='A sample API')
```

APIFlask:

```python
app = APIFlask(__name__, version='1.0', title='Sample API', description='A sample API')
```

But APIFlask provides [extensive configuration options](/configuration) for the API documentation.

## Postman Support & Field Masks

=== "Flask-RESTPlus"

    Flask-RESTPlus provides a built-in feature to generate Postman collections:

    ```python
    from flask import json

    from myapp import api

    urlvars = False  # Build query strings in URLs
    swagger = True  # Export Swagger specifications
    data = api.as_postman(urlvars=urlvars, swagger=swagger)
    print(json.dumps(data))
    ```

    It also supports partial object fetching (aka. fields mask) by supplying a custom header in the request.

=== "APIFlask"

    APIFlask does not provide these features yet.
    [Create an feature request](https://github.com/apiflask/apiflask/issues/new?assignees=&labels=feature&projects=&template=feature-request.md&title=) if you need it.
