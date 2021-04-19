# Comparison and Motivations

APIFlask starts as a fork of APIFairy (which share similar APIs with flask-smorest)
and is inspired by flask-smorest and FastAPI. So, what are the differences between
APIFlask and APIFairy/flask-smorest/FastAPI?

In a word, I try to provide an elegant (act as a framework, no need to instantiate
additional extension object) and simple (more automation support for OpenAPI/API
documentation) solution for creating web APIs with Flask. Here is a summary of the
differences between APIFlask and similar projects.

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

You only need to use `APIFlask` class to replace the `Flask` class:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
```

The key reasons behind making APIFlask a framework instead of a Flask
extension is:

- I have to rewrite the `Flask` class to ensure natural order of the arguments
injected into the view function.
- I have to rewrite the `Flask` and the `Blueprint` class to add route shortcuts.

See the following two sections for more details.

### A natural order of view arguments

By acting as a framework on top of Flask, APIFlask can overwrite the way Flask 
passes path arguments to view functions from keyword arguments to positional
arguments.

Assume a view like this:

```python
@app.get('/<category>/articles/<int:article_id>')  # category, article_id
@input(ArticleQuerySchema, location='query')  # query
@input(ArticleInSchema)  # data
def get_article(category, article_id, query, data):
    pass
```

With APIFlask, you can accept the arguments in the view function in a natural way
(from left to right, from top to bottom):

```python
def get_article(category, article_id, query, data)
```

However, with APIFairy, Flask-Smorest or Webargs, the path variables
(`category` and `article_id`) need to be declared after the input data:

```python
def get_article(query, data, category, article_id)
```

!!! note
    I achieve this by overwriting Flask's `Flask.dispatch_request` method [at this line](https://github.com/greyli/apiflask/blob/master/apiflask/app.py#L290). If you have a
    better solution, feel free to submit a PR.

### Route shortcuts

APIFlask added some route shortcuts (`app.get()`, `app.post()` , etc) for `app.route(..., methods=['GET/POST...'])`.

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
- Add authentication error response (401) for view functions that use `auth_required` decorator
- Add response schema for potential error responses of view function passed with `doc` decorator. For example, `doc(responses=[404, 405])` (I'm considering rename the `responses` argument to `errors` or `error_responses`, what do you think?).

!!! tip
    These automation behaviors can be changed with related
    [configuration variables](/configuration).

### More features compare with APIFairy

- Add a `doc` decorator to allow set the OpenAPI spec for view functions in an explicit way.
- Support more OpenAPI fields (all fields from `info`, `servers`, response/requestBody/parameters `example`, path `deprecated`, etc).
- Support to customize the API documentation config and CDN URLs.
- Return JSON response for all HTTP errors and Auth errors as default.

## APIFlask vs FastAPI

- FastAPI is nearly three years old, while APIFlask is only three months old. The former
is production-ready. The latter is still in the early stage.
- For the web part, FastAPI builts on top of Starlette, while APIFlask builts on top of
Flask.
- For the data part (serialization/deserialization, OpenAPI support), FastAPI relies
on Pydantic, while APIFlask uses marshmallow-code projects (Marshmallow, Webargs, APISpec).
- APIFlask builts on top of Flask, so it's compatible with Flask extensions.
- FastAPI support async. APIFlask will have basic async support after Flask 2.0 is released.
- APIFlask provides more decorators to help organize things better.
- FastAPI injects the input data as an object, while APIFlask passes it as a dict.

!!! tip
    Flask 2.0 will have basic async support and I also consider add support to change
    the base Flask to the async version of Flask, Quart.

!!! note
    I have to admit, I know very little about FastAPI other than the introduction
    on its README. I will try to learn more about it, and then I will update this
    section.

## APIFlask vs Flask-RESTful

Flask-RESTful's latest release is in 2014. Besides, its core components were
deprecated, see [this issue](https://github.com/flask-restful/flask-restful/issues/883) for more details.
