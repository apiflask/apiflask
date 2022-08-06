# Comparison and Motivations

APIFlask starts as a fork of APIFairy (which share similar APIs with flask-smorest)
and is inspired by flask-smorest and FastAPI. So, what are the differences between
APIFlask and APIFairy/flask-smorest/FastAPI?

In a word, I try to provide an elegant (act as a framework, no need to instantiate
additional extension object) and simple (more automation support for OpenAPI/API
documentation) solution for creating web APIs with Flask. Here is a summary of the
differences between APIFlask and similar projects.


## APIFlask vs FastAPI

- For the web part, FastAPI builds on top of Starlette, while APIFlask builts on top of
  Flask.
- For the data part (serialization/deserialization, OpenAPI support), FastAPI relies
  on Pydantic, while APIFlask uses marshmallow-code projects (marshmallow, webargs, apispec).
- APIFlask builds on top of Flask, so it's compatible with Flask extensions.
- FastAPI support async. APIFlask will have the basic async support with Flask 2.0.
- APIFlask provides more decorators to help organize things better.
- FastAPI injects the input data as an object, while APIFlask passes it as a dict.
- APIFlask has built-in class-based views support based on Flask's `MethodView`.
- On top of Swagger UI and Redoc, APIFlask supports more API documentation tools:
  Elements, RapiDoc, and RapiPDF.


## APIFlask vs APIFairy/flask-smorest


### It's a framework (and why?)

Although APIFlask is a thin wrapper on top of Flask, it's actually a framework.
Thus, there is no need to instantiate additional extension object:

```python
from flask import Flask
from flask_api_extension import APIExtension

app = Flask(__name__)
api = APIExtension(app)
```

You only need to use the `APIFlask` class to replace the `Flask` class:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
```

The key reasons behind making APIFlask a framework instead of a Flask
extension is:

- I have to rewrite the `Flask` class to ensure the natural order of the arguments
injected into the view function.
- I have to rewrite the `Flask` and the `Blueprint` class to add route shortcuts.
- Possible to add more high-level features, such as support returning list as JSON response.

See the following two sections for more details.


### A natural order of view arguments

By acting as a framework on top of Flask, APIFlask can overwrite the way Flask
passes path arguments to view functions from keyword arguments to positional
arguments.

Assume a view like this:

```python
@app.get('/<category>/articles/<int:article_id>')  # category, article_id
@app.input(ArticleQuery, location='query')  # query
@app.input(ArticleIn)  # data
def get_article(category, article_id, query, data):
    pass
```

With APIFlask, you can accept the arguments in the view function in a natural way
(from left to right, from top to bottom):

```python
def get_article(category, article_id, query, data)
```

However, with APIFairy, Flask-Smorest, or webargs, the path variables
(`category` and `article_id`) need to be declared after the input data:

```python
def get_article(query, data, category, article_id)
```


### Route shortcuts

APIFlask added some route shortcuts (`app.get()`, `app.post()` , etc) for
`app.route(..., methods=['GET/POST...'])`.

Instead of doing something like this:

```python
@app.route('/pets', methods=['POST'])
def create_pet():
    pass
```

You can just use `@app.post()`:

```python
@app.post('/pets')
def create_pet():
    pass
```

!!! tip

    Flask will have original support for these route shortcuts in the 2.0 version.


### More automation for OpenAPI generating

- Add an auto-summary for the view function based on the name of view functions.
- Add success response (200) for a bare view function that only uses route decorators.
- Add validation error response (400) for view functions that use `input` decorator.
- Add authentication error response (401) for view functions that use `auth_required` decorator.
- Add 404 response for view functions that contain URL variables.
- Add response schema for potential error responses of view function passed with `doc` decorator. For example, `doc(responses=[404, 405])`.
- etc.

!!! tip

    These automation behaviors can be changed with related
    [configuration variables](/configuration).


### More features compare with APIFairy

- Add a `doc` decorator to allow set the OpenAPI spec for view functions in an explicit way.
- Support more OpenAPI fields (all fields from `info`, `servers`, response/requestBody/parameters `example`, path `deprecated`, etc).
- Support to customize the API documentation config and CDN URLs.
- Return JSON response for all HTTP errors and Auth errors as default.
- Class-based view support.
- etc.
