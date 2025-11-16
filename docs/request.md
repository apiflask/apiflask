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

!!! tip

    Cookie parameters don't work well with OpenAPI, see this [issue](https://github.com/apiflask/apiflask/issues/705) for more details.

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
def hello(headers_data, query_data, json_data):
    pass
```


## Request body content types

In the generated OpenAPI spec, the request body content type is set based on the input location you declared.

- `json`: `application/json`
- `form`: `application/x-www-form-urlencoded`
- `files`: `multipart/form-data`
- `form_and_files`: `multipart/form-data`
- `json_or_form`: `application/json` and `application/x-www-form-urlencoded`. For this location, APIFlask will
  try to parse the request body as JSON first, if it fails, it will try to parse it as form data. The OpenAPI spec
  will show both content types, for example:

    ```yaml
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              ...
        application/x-www-form-urlencoded:
          schema:
            type: object
            properties:
              ...
    ```


## Request body validating

When you declared an input with `app.input` decorator, APIFlask (webargs) will get the data
from specified location and validate it against the schema definition.

If the parsing and validating success, the data will pass to the view function as keyword argument
named `{location}_data`:

```python
@app.get('/')
@app.input(FooQuery, location='query')  # query
@app.input(FooIn, location='json')  # data
def hello(query_data, json_data):
    pass
```

If you also defined some URL variables, they wll also be passed as keyword arguments:

```python
@app.get('/<category>/articles/<int:article_id>')  # category, article_id
@app.input(ArticleQuery, location='query')  # query
@app.input(ArticleIn, location='json')  # data
def get_article(category, article_id, query_data, json_data):
    pass
```

!!! tip

    Notice the argument name for URL variables (`category, article_id`) must match the variable name.

If validation failed, a 400 error response will be returned automatically. Like any other error response,
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

The default status code of validation error is 422, you can change this via the
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
def hello(query_data, json_data):
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
def hello(query_data, json_data):
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
def upload_image(files_data):
    f = files_data['image']

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
def create_profile(form_and_files_data):
    avatar_file = form_and_files_data['avatar']
    name = form_and_files_data['name']

    avatar_filename = secure_filename(avatar_file.filename)
    avatar_file.save(os.path.join(the_path_to_uploads, avatar_filename))

    profile = Profile(name=name, avatar_filename=avatar_filename)
    # ...
    return {'message': 'profile created.'}
```

In the current implementation, `files` location data will also include
the form data (equals to `form_and_files`).

!!! notes

    From APIFlask 2.1.0, you can use the `FileType` and `FileSize` validators
    to validate file type and size:

    ```python
    from apiflask.validators import FileType, FileSize

    class Image(Schema):
        image = File(validate=[FileType(['.png', '.jpg', '.jpeg', '.gif']), FileSize(max='5 MB')])
    ```


## Request examples

You can set request examples for OpenAPI spec with the `example` and `examples`
parameters, see [this section](/openapi/#response-and-request-example) in the
OpenAPI Generating chapter for more details.
