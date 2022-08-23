# Request Handling

Read [this section](/usage/#use-appinput-to-validate-and-deserialize-request-data)
in the Basic Usage chapter first for the basics on request handling.

Basic concepts on request handling:

- APIFlask uses [webargs](https://github.com/marshmallow-code/webargs) to handle request
  parsing and validating.
- Use one or more [`app.input()`](/api/app/#apiflask.scaffold.APIScaffold.input) to declare
  an input source, and use the `location` to declare the input location.
- If the parsing and validating success, the data will pass to the view function.
  Otherwise, a 400 error response will be returned automatically.


## Request locations

The following location are supported:

- `json` (default)
- `form`
- `query` (same with `querystring`)
- `path` (same with `view_args`, added in APIFlask 1.0.2)
- `cookies`
- `headers`
- `files`
- `form_and_files`
- `json_or_form`

You can declare multiple input data with multiple `app.input` decorators. However,
you can only declare one body location for your view function, one of:

- `json`
- `form`
- `files`
- `form_and_files`
- `json_or_form`

```python
@app.get('/')
@app.input(FooHeader, location='headers')  # header
@app.input(FooQuery, location='query')  # query string
@app.input(FooIn, location='json')  # JSON data (body location)
def hello(headers, query, data):
    pass
```


## Request body validating

When you declared an input with `app.input` decorator, APIFlask (webargs) will get the data
from specified location and validate it against the schema definition.

If the parsing and validating success, the data will pass to the view function. When you
declared multiple inputs, the order will be from top to bottom:

```python
@app.get('/')
@app.input(FooQuery, location='query')  # query
@app.input(FooIn, location='json')  # data
def hello(query, data):
    pass
```

!!! tip

    The argument name (`query, data`) in the view function is defined by you, you can use anything you like.

If you also defined some URL variables, the order will be from left to right (plus from top to bottom):

```python
@app.get('/<category>/articles/<int:article_id>')  # category, article_id
@app.input(ArticleQuery, location='query')  # query
@app.input(ArticleIn, location='json')  # data
def get_article(category, article_id, query, data):
    pass
```

!!! tip

    Notice the argument name for URL variables (`category, article_id`) must match the variable name.

Otherwise, a 400 error response will be returned automatically. Like any other error response,
this error response will contain `message` and `detail` fields:

- `message`

The value will be `Validation error`, you can change this via the config
`VALIDATION_ERROR_DESCRIPTION`.

- `detail`

The detail field contains the validation information in the following format:

```python
"<location>": {
    "<field_name>": ["<error_message>", ...],
    "<field_name>": ["<error_message>", ...],
    ...
},
"<location>": {
    ...
},
...
```

The value of `<location>` is where the validation error happened.

- status code

The default status code of validation error is 400, you can change this via the
config `VALIDATION_ERROR_STATUS_CODE`.


## Dict schema

When passing the schema to `app.input`, you can also use a dict instead of a schema class:

```python
from apiflask.fields import Integer


@app.get('/')
@app.input(
    {'page': Integer(load_default=1), 'per_page': Integer(load_default=10)},
    location='query'
)
@app.input(FooIn, location='json')
def hello(query, data):
    pass
```

The dict schema's name will be something like `"Generated"`. To specify a schema
name, use the `schema_name` parameter:

```python hl_lines="7"
from apiflask.fields import Integer


@app.get('/')
@app.input(
    {'page': Integer(load_default=1), 'per_page': Integer(load_default=10)},
    location='query',
    schema_name='PaginationQuery'
)
@app.input(FooIn, location='json')
def hello(query, data):
    pass
```

However, we recommend creating a schema class whenever possible to make the
code easy to read and reuse.


## File uploading

!!! warning "Version >= 1.0.0"

    This feature was added in the [version 1.0.0](/changelog/#version-100).

You can use [`apiflask.fields.File`](/api/fields/#apiflask.fields.File) to create a file
field in the input schema and use the `files` location for `app.input`:

```python
import os

from werkzeug.utils import secure_filename
from apiflask.fields import File


class Image(Schema):
    image = File()


@app.post('/images')
@app.input(Image, location='files')
def upload_image(data):
    f = data['image']

    filename = secure_filename(f.filename)
    f.save(os.path.join(the_path_to_uploads, filename))

    return {'message': f'file {filename} saved.'}
```

!!! tip

    Here we use `secure_filename` to clean the filename, notice it will only keep ASCII characters.
    You may want to create a random filename for the newly uploaded file, this
    [SO answer](https://stackoverflow.com/a/44992275/5511849) may be helpful.

The file object is an instance of `werkzeug.datastructures.FileStorage`, see more details
[in Werkzeug's docs][_docs].

[_docs]: https://werkzeug.palletsprojects.com/datastructures/#werkzeug.datastructures.FileStorage

Use `form_and_files` location if you want to put both files
and other normal fields in one schema:

```python
import os

from werkzeug.utils import secure_filename
from apiflask.fields import String, File


class ProfileIn(Schema):
    name = String()
    avatar = File()

@app.post('/profiles')
@app.input(ProfileIn, location='form_and_files')
def create_profile(data):
    avatar_file = data['avatar']
    name = data['name']

    avatar_filename = secure_filename(avatar_file.filename)
    avatar_file.save(os.path.join(the_path_to_uploads, avatar_filename))

    profile = Profile(name=name, avatar_filename=avatar_filename)
    # ...
    return {'message': 'profile created.'}
```

In the current implementation, `files` location data will also include
the form data (equals to `form_and_files`).

!!! notes

    Validators for the file field will be available in the version 1.1
    ([#253](https://github.com/apiflask/apiflask/issues/253)). For now,
    you can manually validate the file in the view function or the schema:

    ```python
    class Image(Schema):
        image = File(validate=lambda f: f.mimetype in ['image/jpeg', 'image/png'])
    ```


## Request examples

You can set request examples for OpenAPI spec with the `example` and `examples`
parameters, see [this section](/openapi/#response-and-request-example) in the
OpenAPI Generating chapter for more details.
