# OpenAPI Generating

[OpenAPI](https://github.com/OAI/OpenAPI-Specification) (originally known as the
Swagger Specification) is a popular description specification for REST API. APIFlask
has built-in support for it. This chapter will cover the basic usage of OpenAPI generating
in APIFlask.

!!! note "Code-first or Design-first"

    There are two approaches when working with OpenAPI: Code-first and Design-first.
    APIFlask currently only supports the first way. It generates the OpenAPI spec
    for you after you write the code. We will try to support the Design-first
    approach after the 1.0 version is released.


## A general view of the OpenAPI support

APIFlask collects the information from the configuration values, registered routes, and
the information you passed through decorators, then generates the OpenAPI spec based
on these information.

Field Name | How APIFlask generating it  | How to customize it
-----------|-----------------------------|---------------------
openapi    | - | Use the configuration variable [`OPENAPI_VERSION`](/configuration/#openapi_version)
info | - | See *[Meta information](#meta-information)*
servers | - | Use the configuration variable [`SERVERS`](/configuration/#servers)
paths | Generate based on the routes and decorators | Use `input`, `output`, `doc` decorators and docstring
components | Generate from data schema | -
security | Generate security info from the auth objects | Use the `auth_required` decorator
tags | Generate from blueprint names | See *[Tags](#tags)*
externalDocs | - | Use the configuration variable [`EXTERNAL_DOCS`](/configuration/#external_docs)

It provides three ways to obtain the spec document file:

- An `app.spec` attribute that returns the dict spec.
- A spec endpoint that serves the spec.
- A `flask spec` command to output the spec to stdout or file.

Besides, it also provides an `app.spec_processor` decorator, which you can use to register
a spec process function to update the spec before it returns. See
*[Register a spec processor](#register-a-spec-processor)* for more details.


### Automation behaviors

When generating the OpenAPI spec from your code, APIFlask has some automation behaviors:

- Generate a default operation summary from the name of the view function.
- Generate a default operation description from the docstring of the view function.
- Generate tags from the name of blueprints.
- Add a default 200 response for any views registered to the application.
- Add a 400 response if the view is decorated with `app.input`.
- Add a 401 response if the view is decorated with `app.auth_required`.
- Add a 404 response if the view's URL rule contains variables.

All these automation behaviors can be disabled with
[the corresponding configurations](/configuration/#automation-behavior-control).


### The spec format

The default format of the OpenAPI spec is JSON, while YAML is also supported.
If you want to enable the YAML support, install APIFlask with the `yaml` extra
(it will install `PyYAML`):

```
$ pip install apiflask[yaml]
```

Now you can change the format via the `SPEC_FORMAT` config:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] = 'yaml'
```

The default URL path for spec endpoint is `/openapi.json`, you may also want to update
it when you want to use YAML format:

```python hl_lines="3"
from apiflask import APIFlask

app = APIFlask(__name__, spec_path='/openapi.yaml')
app.config['SPEC_FORMAT'] = 'yaml'
```

The `SPEC_FORMAT` config will also control the spec format output of the `flask spec` command.


### The indentation of the JSON spec

When you view the spec from your browser via `/openapi.json`, if you enabled the
debug mode or set the configuration variable `JSONIFY_PRETTYPRINT_REGULAR` to
`True`, the indentation will set to `2`. Otherwise, the JSON spec will be sent
without indentation and spaces to save the bandwidth and speed the request.

The indentation of the local spec file is enabled by default. The default indentation
is the default value of the `LOCAL_SPEC_JSON_INDENT` config (i.e., `2`). When you
use the `flask spec` command, you can change the indentation with the `--indent`
or `-i` option.

The indentation of the YAML spec is always `2`, and it can't be changed for now.


## The `app.spec` attribute

You can get the spec in dict format with the `app.spec` attribute. It will always return the latest spec:

```python
>>> from apiflask import APIFlask
>>> app = APIFlask(__name__)
>>> app.spec
{'info': {'title': 'APIFlask', 'version': '0.1.0'}, 'tags': [], 'paths': OrderedDict(), 'openapi': '3.0.3'}
>>> @app.get('/')
... def hello():
...     return {'message': 'Hello'}
...
>>> app.spec
{'info': {'title': 'APIFlask', 'version': '0.1.0'}, 'tags': [], 'paths': OrderedDict([('/', {'get': {'parameters': [], 'responses': OrderedDict([('200', {'content': {'application/json': {'schema': {}}}, 'description': 'Successful response'})]), 'summary': 'Hello'}})]), 'openapi': '3.0.3'}
>>>
```


## The spec endpoint

By default, the spec is in JSON format and available at the URL path `/openapi.json`,
you can change the URL rule of the spec endpoint with the `spec_path` parameter:

```python
from apiflask import APIFlask

app = APIFlask(__name__, spec_path='/spec')
```

Then the spec will be available at http://localhost:5000/spec.

!!! tip

    You can configure the MIME type of the spec response with the configuration
    variable `YAML_SPEC_MIMETYPE` and `JSON_SPEC_MIMETYPE`, see details in the
    [configuration docs](/configuration#json_spec_mimetype).


## The `flask spec` command

!!! warning "Version >= 0.7.0"

    This feature was added in the [version 0.7.0](/changelog/#version-070).

The `flask spec` command will output the spec to stdout when you execute
the command:

```
$ flask spec
```

See the output of `flask spec --help` for the full API reference of this
command:

```
$ flask spec --help
```

You can skip the next three sections if you have executed the above command.


### Output the spec to a file

If you provide a path with the `--output` or `-o` option, APIFlask will write
the spec to the given path:

```
$ flask spec --output openapi.json
```

!!! note "No such file or directory?"

    If the given path does not exist, you have to create the directory by yourself,
    then APIFlask will create the file for you.

You can also set the path with the configuration variable `LOCAL_SPEC_PATH`, then the
value will be used in `flask spec` command when the `--output/-o` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
```

```
$ flask spec
```


### Change the spec format

Similarly, the spec format can be set with the `--format` or `-f` option
(defaults to `json`):

```
$ flask spec --format json
```

You can also set the format with the configuration variable `SPEC_FORMAT` (defaults
to `'json'`), then the value will be used in `flask spec` command when the
`--format/-f` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] = 'yaml'
```

```
$ flask spec
```


### Change the indentation of the local JSON spec

For the local spec file, the indentation is always needed for readability and
easy to trace the changes. The indentation can be set with the `--indent` or
`-i` option:

```
$ flask spec --indent 4
```

You can also set the indentation with the configuration variable
`LOCAL_SPEC_JSON_INDENT` (defaults to `2`), then the value will be used in
the `flask spec` command when the `--indent/-i` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)
app.config['LOCAL_SPEC_JSON_INDENT'] = 4
```

```
$ flask spec
```


## Keep the local spec in sync

!!! warning "Version >= 0.7.0"

    This feature was added in the [version 0.7.0](/changelog/#version-070).

With the `flask spec` command, you can easily generate the spec to a local file.
While it will be handy if the spec file is in sync with the project code.
To achieve this, you need to set a path to the config `LOCAL_SPEC_PATH`,
then enable the sync by setting the config `SYNC_LOCAL_SPEC` to `True`:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
```

!!! warning

    If the path you passed is relative, do not put a leading slash in it.

APIFlask will create the file at your current working directory (where you execute the
`flask run` command). We recommend using an absolute path. For example, you can use
`app.root_path`, which stores the absolute root path to your app module:

```python
from pathlib import Path

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = Path(app.root_path) / 'openapi.json'
```

!!! tip

    You can also use
    [`app.instance_path`](https://flask.palletsprojects.com/config/#instance-folders){target=_blank},
    it will be useful if your app is inside a package since it returns the path to
    the instance folder located at the project root path.

Or use the `os` module:

```python
import os

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')
```

You can also find the project root path manually based on the current module's
`__file__` variable when you are using an application factory. In this case,
you normally put the config into a file called `config.py` located at the
project root path:

```
- my_project/ -> project folder
  - app/ -> application package
  - config.py -> config file
```

So you can find the base path like this:

```python
from pathlib import Path

base_path = Path(__file__).parent
# you may need to use the following if your config module is
# inside the application package:
# base_path = Path(__file__).parent.parent

SYNC_LOCAL_SPEC = True
LOCAL_SPEC_PATH = base_path / 'openapi.json'
```

Or use the `os` module:

```python
import os

base_path = os.path.dirname(__file__)
# you may need to use the following if your config module is
# inside the application package:
# base_path = os.path.dirname(os.path.dirname(__file__))

SYNC_LOCAL_SPEC = True
LOCAL_SPEC_PATH = os.path.join(base_path, 'openapi.json')
```


## Meta information

The `title` and `version` field can be passed when creating the `APIFlask` instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__, title='My API', version='1.0')
```

Other fields in the `info` object are available with the following configuration
variables:

- `DESCRIPTION`
- `TERMS_OF_SERVICE`
- `CONTACT`
- `LICENSE`

You can also set all these four fields with [`INFO`](/configuration#info).

See the [OpenAPI fields](/configuration#openAPI-fields) section in the configuration
docs for the details.


## Tags

By default, the `tag` object is generated automatically based on the blueprints:

- A blueprint generates a tag, the name of the blueprint in title form will become
the name of the tag.
- All routes under the blueprint will be tagged with the corresponding tag automatically.

If you want to use a custom tag name for a blueprint or want to add more details for
the tag, you can use the `APIBlueprint(tag=...)` parameter to pass a new name:

```python
from apiflask import APIBlueprint

bp = APIBlueprint('foo', __name__, tag='New Name')
```

This parameter also accepts a dict:

```python
bp = APIBlueprint('foo', __name__, tag={'name': 'New Name', 'description': 'blah...'})
```

If you don't like this blueprint-based tagging system, surely you can do it manually.
You can pass a list of tag names to the configuration variable `TAGS`:

```python
app.config['TAGS'] = ['foo', 'bar', 'baz']
```

It also accepts a list of dicts if you want to add details about tags:

```python
app.config['TAGS'] = [
    {'name': 'foo', 'description': 'The description of foo'},
    {'name': 'bar', 'description': 'The description of bar'},
    {'name': 'baz', 'description': 'The description of baz'}
]
```

!!! tip

    The `app.tags` attribute is equals to the configuration variable `TAGS`, so you
    can also use:

    ```python
    app.tags = ['foo', 'bar', 'baz']
    ```

When the `TAGS` is set, you can now add tags for each route (OpenAPI operation) with
the `doc` decorator, see [Operation `tags`](#operation-tags)


## Path items and operations

Most of the information in `path` and `operation` object is generated from
your view functions or view classes automatically, while you may want to change some of them.


### Operation `responses`

The operation `responses` will be generated when you add the `output` decorator
on the view function:

```python hl_lines="2"
@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    return pets[pet_id]
```

You can set the `description` and `status_code` (default to `200`) through the
corresponding parameters in the `output` decorator:

```python hl_lines="2"
@app.get('/pets/<int:pet_id>')
@app.output(PetOut, status_code=200, description='Output data of a pet')
def get_pet(pet_id):
    return pets[pet_id]
```

There are some automatic behaviors on operation `responses` object:

- If the `input` decorator is added to the view function, APIFlask will add
a `400` response.
- When the `auth_required` decorator is added to the view function, APIFlask will
add a `401` response.
- If the view function only use the route decorator, APIFlask will add a default
`200` response.
- If the route URL contains a variable (e.g., `'/pets/<int:pet_id>'`), APIFlask will
add a `404` response (Version >= 0.8).

You can disable these behaviors or configure them through related
[configuration variables](/configuration#automation-behavior-control).


### Operation `requestBody` and `parameters`

The operation `requestBody` will be generated when you add the `input` decorator
on the view function:

```python hl_lines="2"
@app.post('/pets')
@app.input(PetIn)
def create_pet(pet_id):
    pass
```

When you specify a request data location other than `json`, the operation `parameters`
will be generated instead:

```python hl_lines="2"
@app.get('/pets')
@app.input(PetQuery, location='query')
def get_pets():
    pass
```


### Operation `summary` and `description`

By default, APIFlask will use the name of the view function as the operation summary.
If your view function is named with `get_pet`, then the `summary` will be "Get Pet".

If the view function has docstring, then the first line of the docstring will be used
as the `summary`, the lines after the empty line of the docstring will be used as
the `description`.

!!! note "The precedence of summary setting"

    ```
    @app.doc(summary='blah') > the first line of docstring > the view function name
    ```

Here is an example of set `summary` and `description` with docstring:

```python hl_lines="3 5"
@app.get('/hello')
def hello():
    """Say hello

    Some description for the /hello
    """
    return 'Hello'
```


### Response and request `schema`

APIFlask (with apispec) will generate the operation `schema` object from the data schema
you passed.

To set the OpenAPI spec for schema fields, you can pass a dict with the `metadata` keyword:

```python
class PetIn(Schema):
    name = String(metadata={'description': 'The name of the pet.'})
```

You can pass the OpenAPI schema field name as the key in this metadata dict. Currently,
the following fields are supported:

- `format`
- `title`
- `description`
- `default`
- `multipleOf`
- `maximum`
- `exclusiveMaximum`
- `minimum`
- `exclusiveMinimum`
- `maxLength`
- `minLength`
- `pattern`
- `maxItems`
- `minItems`
- `uniqueItems`
- `maxProperties`
- `minProperties`
- `required`
- `enum`
- `type`
- `items`
- `allOf`
- `properties`
- `additionalProperties`
- `readOnly`
- `writeOnly`
- `xml`
- `externalDocs`
- `example`
- `nullable`
- `deprecated`
- Any custom field starts with `x-` prefix

See the details of these fields at
[OpenAPI docs](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#schemaObject).

However, most of these fields will be generated when you set up the schema field.
For example, if you set `required` to `True`, pass a `Length(0, 10)` validator
to `validate`:

```python
from apiflask import Schema
from apiflask.fields import String

class PetIn(Schema):
    name = String(
        required=True,
        validate=Length(0, 10),
        metatdata={'description': 'The name of the pet.'}
     )
```

Then in the final spec, the `type`, `maxLength`, `minLength` and `required` field will have
the right value:

```json
"PetIn": {
    "properties": {
        "name": {
            "description": "The name of the pet.",
            "maxLength": 10,
            "minLength": 0,
            "type": "string"
        }
    },
    "required": [
        "name"
    ],
    "type": "object"
}
```

Normally, you only need to set the following fields manually with the `metadata` dict:

- `description`: Some description for this field.
- `title`: The title of the field.
- `example`: A example value for this field (property-level example).
- `deprecated`: If true, indicates this field is deprecated.
- `externalDocs`: A link points to the external documentation for this field.
- `xml`: Adds additional metadata to describe the XML representation format of this field.
See details in
*[OpenAPI XML object](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#xmlObject)*.

!!! tip

    If the schema class' name ends with `Schema`, then it will be stripped in the spec.


### Response and request example

When rendering the spec in the API documentation, the docs tool will generate a default
example for you. If you want to add a custom example, you can use the `example` parameter to pass a dict as the response `example` in the `input`/`output` decorator:

```python hl_lines="6"
from apiflask import APIFlask, input

app = APIFlask(__name__)

@app.post('/pets')
@app.input(PetIn, example={'name': 'foo', 'category': 'cat'})
def create_pet():
    pass
```

For multiple examples, use the `examples` parameter and pass a dict of dict, every
example dict maps a unique name:

```python hl_lines="17"
from apiflask import APIFlask, output

app = APIFlask(__name__)

examples = {
    'example foo': {
        'summary': 'an example of foo',
        'value': {'name': 'foo', 'category': 'cat', 'id': 1}
    },
    'example bar': {
        'summary': 'an example of bar',
        'value': {'name': 'bar', 'category': 'dog', 'id': 2}
    },
}

@app.get('/pets')
@app.output(PetOut, examples=examples)
def get_pets():
    pass
```

!!! note

    Currently, the `example`/`examples` parameter in the `input` decorator is only
    support JSON body. When you need to set a custom example for query data,
    you can set the field example (property-level example) in the data schema:

    ```python
    class PetQuery(Schema):
        name = String(metadata={'example': 'Flash'})
    ```


## Response `links`

!!! warning "Version >= 0.10.0"

    This feature was added in the [version 0.10.0](/changelog/#version-0100).

You can pass the links with `links` keyword in the `output` decorator:

```python
pet_links = {
    'getAddressByUserId': {
        'operationId': 'getUserAddress',
        'parameters': {
            'userId': '$request.path.id'
        }
    }
}

@app.post('/pets')
@app.output(PetOutSchem, links=pet_links)
def new_pet(data):
    pass
```

Or you can also add links to components then reference it in operation:

```python
links = {
    'getAddressByUserId': {
        'operationId': 'getUserAddress',
        'parameters': {
            'userId': '$request.path.id'
        }
    }
}

@app.spec_processor
def update_spec(spec):
    spec['components']['links'] = links
    return spec


@app.post('/pets')
@app.output(PetOutSchem, links={'getAddressByUserId': {'$ref': '#/components/links/getAddressByUserId'}})
def new_pet(data):
    pass
```


## Use the `doc` decorator

There is also a `doc` decorator that can be used to set operation fields explicitly.


### Operation `summary` and `description`

Here is the example of using the `doc` decorator to set `summary` and `description`:

```python hl_lines="6"
from apiflask import APIFlask, doc

app = APIFlask(__name__)

@app.get('/hello')
@app.doc(summary='Say hello', description='Some description for the /hello')
def hello():
    return 'Hello'
```


### Operation `tags`

When you are using blueprints in your application, APIFlask provides an automatic tagging system,
see [Tags](#tags) for more details.

You only need to set the tag if you are not using a blueprint or you want to control the tags by
yourself. The `tags` parameter accepts a list of tag name string, they should match the values you
passed in `TAGS` config or `app.tags` attribute:

```python hl_lines="2"
@app.get('/')
@app.doc(tags=['Foo'])
def hello():
    return 'Hello'
```


### Alternative operation `responses`

As described above, APIFlask will add some responses based on the decorators you added
on the view function (200, 400, 401, 404). Sometimes you may want to add alternative
responses the view function will return, then you can use the `@app.doc(responses=...)`
parameter, it accepts the following values:

- A list of status code int, for example, `[404, 418]`.
- A dict in a format of `{<STATUS_CODE>: <DESCRIPTION>}`, this will allow you to
set a custom description for each status, for example,
`{404: 'Not Found', 418: 'Blah...'}`. If a response with the same status code is
already exist, the existing description will be overwritten.

```python hl_lines="2"
@app.get('/')
@app.doc(responses=[204, 404])
def hello():
    return 'Hello'
```


### Mark an operation as `deprecated`

You can mark an operation as deprecated with the `deprecated` parameter:

```python hl_lines="2"
@app.get('/')
@app.doc(deprecated=True)
def hello():
    return 'Hello'
```


### Set `operationId`

!!! warning "Version >= 0.10.0"

    This feature was added in the [version 0.10.0](/changelog/#version-0100).

You can set `operationId` for a view funtion (operation) with the `operation_id` parameter:

```python hl_lines="2"
@app.get('/')
@app.doc(operation_id='myCustomHello')
def hello():
    return 'Hello'
```

APIFlask supports to generate operationId automatically. The auto-generating behavior is disabled
as default, you can enable it by setting the following configuration variable to `True`:

```python
app.config['AUTO_OPERATION_ID'] = True
```

The auto-operationId will in the format of `{HTTP method}_{endpoint of the view}` (e.g. `get_hello`).


## Security information

APIFlask will generate the `security` object and operation `security` field based on
the auth object passed with the `auth_required` decorator:

```python hl_lines="4 7"
from apiflask import APIFlask, HTTPTokenAuth, auth_required

app = APIFlask(__name__)
auth = HTTPTokenAuth()

@app.get('/')
@app.auth_required(auth)
def hello():
    return 'Hello'!
```

You can use the `description` parameter to set the description for auth objects:

```python hl_lines="4"
from apiflask import APIFlask, HTTPTokenAuth

app = APIFlask(__name__)
auth = HTTPTokenAuth(description='some description')
```


## Disable the OpenAPI support


### Disable globally

If you want to disable the whole OpenAPI support for the whole application, you
can set `enable_openapi` parameter to `False` when creating the `APIFlask` instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__, enable_openapi=False)
```

!!! tip

    If you only need to disable the API documentation, see
    *[Disable the API documentations globally](/api-docs/#disable-the-api-documentations-globally)*.


### Disable for specific blueprints

To hide blueprints from API documentations (and OpenAPI spec), you can
set `enable_openapi` parameter to `False` when creating the `APIBlueprint` instance:

```python
from apiflask import APIBlueprint

bp = APIBlueprint('foo', __name__, enable_openapi=False)
```

!!! tip

    APIFlask will skip a blueprint if the blueprint is created by other Flask
    extensions.


### Disable for specific view functions

To hide a view function from API documentations (and OpenAPI spec), you
can set the `hide` parameter to `True` in the `doc` decorator:

```python hl_lines="6"
from apiflask import APIFlask, doc

app = APIFlask(__name__)

@app.get('/secret')
@app.doc(hide=True)
def some_secret():
    return ''
```

!!! note

    By default, APIFlask will add a view function into API documentations
    (and OpenAPI spec) even if the view function doesn't use `input`, `output`,
    and `doc` decorator. If you want to disable this behavior, set configruration
    variable `AUTO_200_RESPONSE` to `False`:

    ```python
    app.config['AUTO_200_RESPONSE'] = False
    ```


## Register a spec processor

You can register a function with the `app.spec_processor` decorator to update the
spec. The callback function should accept the spec as an argument and return it
in the end. The callback function will be called when generating the spec file.

```python
from apiflask import APIFlask

app = APIFlask(__name__)

@app.spec_processor
def update_spec(spec):
    spec['info']['title'] = 'Updated Title'
    return spec
```

Notice the format of the spec depends on the value of the configuration
variable `SPEC_FORMAT` (defaults to `'json'`):

- `'json'` -> dict
- `'yaml'` -> string

Check out [the example application](https://github.com/apiflask/apiflask/tree/main/examples/openapi/app.py)
for OpenAPI support, see [the examples page](/examples) for running the example application.
