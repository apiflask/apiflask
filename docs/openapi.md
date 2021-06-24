# OpenAPI Generating

[OpenAPI](https://github.com/OAI/OpenAPI-Specification) (originally known as the
Swagger Specification) is a popular description specification for REST API. APIFlask
has built-in support for it. This chapter will cover the basic usage of OpenAPI generating
in APIFlask.

!!! note "Code-first or Design-first"

    There are two approachs when working with OpenAPI: Code-first and Design-first.
    APIFlask currently only support the last way. It generates the OpenAPI spec
    for you after you write the code. We will try to support the Design-first
    approach after the 1.0 version is released.


## A general view of the OpenAPI support

APIFlask collects the information from the configuration values, reigistered routes, and
the information you passed through decorators, then generates the OpenAPI spec based
on these information.

Field Name | How APIFlask generating it  | How to customize it
-----------|-----------------------------|---------------------
openapi    | - | Use the configuration variable [`OPENAPI_VERSION`](/configuration/#openapi_version)
info | - | See *[Meta information](#meta-information)*
servers | - | Use the configuration variable [`SERVERS`](/configuration/#servers)
paths | Generate based on the routes and decorators | Use `input`, `output`, `doc` decorators and docstring
components | Generate from data schema | -
security | Generate secuity info from the auth objects | Use the `auth_required` decorator
tags | Generate from blueprint names | See *[Tags](#tags)*
externalDocs | - | Use the configuration variable [`EXTERNAL_DOCS`](/configuration/#external_docs)

It provides two ways to obtain the spec document file:

- A spec endpoint that serves the spec.
- A `flask spec` to output the spec to stdout or file.

Bisides, it also provides a `app.spec_processor` decorator which you can used to register
a spec process function to update the spec before it returns. See
*[Register a spec processor](#register-a-spec-processor)* for more details.


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
app.config['SPEC_FORMAT'] == 'yaml'
```

This config will also control the format output by the `flask spec` command.


### The indentation of JSON spec

When you view the spec from your browser via `/openapi.json`, if you enabled the
debug mode or set the configuration variable `JSONIFY_PRETTYPRINT_REGULAR` to
`True`, the indentation will set to `2`. Otherwise, the JSON spec will be sent
without indentation and spaces to save the bandwidth and speed the request.

The indentation of the local spec file is enabled by default. The default indentation
is the default value of the `LOCAL_SPEC_JSON_INDENT` config (i.e., `2`). When you
use the `flask spec` command, you can change the indentation with the `--indent`
or `-i` option.

The indentation of the YAML spec is always `2`, and it can't be changed for now.


## The spec endpoint

By default, the spec is in JSON format and available at the URL path `/openapi.json`,
you can change the URL rule of the spec endpoint with the `spec_path` parameter:

```python
from apiflask import APIFlask

app = APIFlask(__name__, spec_path='/spec')
```

Then the spec will be available at http://localhost:5000/spec.

!!! tips

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


### Change the indentation of local JSON spec

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

See the [OpenAPI fields](/configuration#openAPI-fields) section in the configuration
docs for the details.


## Tags

By deafult, the `tag` object is generated automatically based on the blueprints:

- A blueprint generate a tag, the name of the bluprint in title form will become
the name of the tag.
- All routes under the blueprint will be tagged with corresponding tag automatically.

If you want to use a custom tag name for blueprint or want to add more details for
the tag, you canuse the `APIBlueprint(tag)` parameter to pass a new name:

```python
from apiflask import APIBlueprint

bp = APIBlueprint(__name__, 'foo', tag='New Name')
```

This parameter also accepts a dict:

```python
bp = APIBlueprint(__name__, 'foo', tag={'name': 'New Name', 'description': 'blah...'})
```

If you don't like this blueprint-based tagging system, surely you can do it manually.
You can pass a list of tag names to the the configuration variable `TAGS`:

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

!!! tips

    The `app.tags` attribute is equels to the configuration variable `TAGS`, so you
    can also use:

    ```python
    app.tags = ['foo', 'bar', 'baz']
    ```  

When the `TAGS` is set, you can now add tags for each route (OpenAPI operation) with
the `doc` decorator, see [Operation `tags`](#operation-tags)


## Path items and operations

Most of the information in `paths` object and `operation` object are generated from
your view functions or view classes automatically, while you may want to change some of them.


### Operation `responses`

The operation `responses` will be generated when you add the `output` decorator
on the view function:

```python hl_lines="2"
@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    return pets[pet_id]
``` 

You can set the `description` and `status_code` (default to `200`) through the
corresponding parameters in the `output` decorator:

```python hl_lines="2"
@app.get('/pets/<int:pet_id>')
@output(PetOutSchema, status_code=200, description='Output data of a pet')
def get_pet(pet_id):
    return pets[pet_id]
```

There are some automatic behaviors on operation `responses` object:

- If the `input` decorator is added on the view function, APIFlask will add
a `400` response. 
- When the `auth_required` decorator is added on the view function, APIFlask will
add a `401` response.
- If the view function only use the route decorator, APIFlask will add a default
`200` response.

You can disable these behavior or configure them through related
[configuration variables](/configuration#automation-behavior-control).


### Operation `requestBody` and `parameters`

The operation `requestBody` will be generated when you add the `input` decorator
on the view function:

```python hl_lines="2"
@app.post('/pets')
@input(PetInSchema)
def create_pet(pet_id):
    pass
``` 

When you specify a request data location other than `json`, the operation `parameters`
will be generated instead:

```python hl_lines="2"
@app.get('/pets')
@input(PetQuerySchema, location='query')
def get_pets():
    pass
```


### Operation `summary` and `description` 

By default, APIFlask will use the name of the view function as operation summary.
If your view function is named with `get_pet`, then the `summary` will be "Get Pet".

If the view function has docstring, then the first line of the docstring will be used
as the `summary`, the lines after the empty line of the docstring will be used as
the `description`.

!!! note "The precedence of summary setting"

    ```
    @doc(summary='blah') > the first line of docstring > the view function name
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

APIFlask (with APISpec) will generate the operation `schema` object from the data schema
you passed.

To set the OpenAPI spec for fields, you can pass a dict with the `metadata` keyword:

```python
class PetInSchema(Schema):
    name = String(metatdata={'description': 'The name of the pet.'})
```

You can pass the OpenAPI schema field name as the key in this metadata dict. Currently,
the following field are supported:

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
- `xml`
- `externalDocs`
- `example`
- Any custom field start with `x-` prefix

See the details of these fields at
[OpenAPI docs](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#schemaObject).

However, the most of these fields will be generated automatically when you set up the
schema field. For example, if you set `required` to `True`, pass a `Length(0, 10)`
validator to `validate`:

```python
from apiflask import Schema
from apiflask.fields import String

class PetInSchema(Schema):
    name = String(
        required=True,
        validate=Length(0, 10),
        metatdata={'description': 'The name of the pet.'}
     )
```

Then in the final spec, the `maxLength`, `minLength` and `required` field will have
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

!!! tips

    If the schema class' name ends with `Schema`, then it will be striped in the spec.


### Response and request example

When redering the spec in API documentation, the docs tool will generate a default
example for you. If you want to add a custom example, you can use the `example` parameter to pass a dict as the response `example` in the `input`/`output` decorator:

```python hl_lines="6"
from apiflask import APIFlask, input

app = APIFlask(__name__)

@app.post('/pets')
@input(PetInSchema, example={'name': 'foo', 'category': 'cat'})
def create_pet():
    pass
```

For multiple examples, use the `examples` parameter and pass a dict of dict, every
example dict maps a unqiue name:

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
@output(PetOutSchema, examples=examples)
def get_pets():
    pass
```

!!! tips

    The `example` metadata passed in the field of the data schema will be overwritten
    with the example passed in the `input` and `output` decorator.


!!! note

    Currently, the `example`/`examples` parameter in the `input` decorator is only
    support JSON body . When you need to set a custom example for query data,
    you can set the field example in the data schema:

    ```python
    class PetQuerySchema(Schema):
        name = String(metadata={'example': 'Flash'})
    ```


## Use the `doc` decorator

There is also a `doc` decorator can be used to set operation fields explicitly.


### Operation `summary` and `description`

Here is the example of using the `doc` decoraotr to set `summary` and `description`:

```python hl_lines="6"
from apiflask import APIFlask, doc

app = APIFlask(__name__)

@app.get('/hello')
@doc(summary='Say hello', description='Some description for the /hello')
def hello():
    return 'Hello'
```


### Operation `tags`

There are two parameters for `tags` available:

- `tag`, accepts a tag name string. It will be used in most cases:

```python hl_lines="2"
@app.get('/')
@doc(tag='Foo')
def hello():
    return 'Hello'
```

- `tags`, accepts a list of tag name string. Only needed when you want to set multiple
tags for one route (OpenAPI operation):

```python hl_lines="2"
@app.get('/')
@doc(tags=['Foo', 'Bar', 'Baz'])
def hello():
    return 'Hello'
```


### Alternative operation `responses`

As described above, APIFlask will add some responses based on the decorators you added
on the view function. Sometime you may want to add alternative responses the view
will return, then you can use the `@doc(responses=...)` parameter, it accepts the
following values:

- A list of status code int, for example, `[404, 418]`.
- A dict in a format of `{<STATUS_CODE>: <DESCRIPTION>}`, this will allow you to
set a custom description for each status, for example,
`{404: 'Not Found', 418: 'Blah...'}`.

```python hl_lines="2"
@app.get('/')
@doc(responses=[204, 404])
def hello():
    return 'Hello'
```


### Mark an operation as `deprecated`

You can mark an operation as deprecated with the `deprecated` parameter:

```python hl_lines="2"
@app.get('/')
@doc(deprecated=True)
def hello():
    return 'Hello'
```


## Security information

APIFlask will generate the `security` object and operation `security` field based on
the auth object passed with the `auth_required` decorator:

```python hl_lines="4 7"
from apiflask import APIFlask, HTTPTokenAuth, auth_required

app = APIFlask(__name__)
auth = HTTPTokenAuth()

@app.get('/')
@auth_required(auth)
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

If you only need to disable API documentations, see.


### Disable for specific blueprints

To hide blueprints from API documentations (and OpenAPI spec), you can
set `enable_openapi` parameter to `False` when creating the `APIBlueprint` instance:

```python
from apiflask import APIBlueprint

bp = APIBlueprint(__name__, 'foo', enable_openapi=False)
```

!!! tips

    APIFlask will skip a blueprint if the blueprint is created by other Flask
    extensions.


### Disable for specific view functions

To hide a view function from API documentations (and OpenAPI spec), you
can set the `hide` parameter to `True` in the `doc` decorator:

```python hl_lines="6"
from apiflask import APIFlask, doc

app = APIFlask(__name__)

@app.get('/secret')
@doc(hide=True)
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

Notice the format of the spec is depends on the the value of configuration
variable `SPEC_FORMAT` (defaults to `'json'`):

- `'json'` -> dict
- `'yaml'` -> string
=======
## Keep the local spec in sync automatically

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

    If the path you passed is a relative path, do not put a leading slash in it.

APIFlask will create the file at your current working directory (where you execute the
`flask run` command). We recommend using an absolute path. For example, you can use
`app.root_path`, which stores the absolute root path to your app module:

```python
from pathlib import Path

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = Path(app.root_path) / 'openapi.json'
```

Or use the `os` module:

```python
import os

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')
```

You can also find the project root path manually based on the current module's
`__file_` variable when you are using an application factory:

```python
from pathlib import Path

base_path = Path(__file__).parent
# you may need to use the following if current module is
# inside the application package:
# base_path = Path(__file__).parent.parent

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = base_path / 'openapi.json'
```

Or use the `os` module:

```python
import os

base_path = os.path.dirname(__file__)
# you may need to use the following if current module is
# inside the application package:
# base_path = os.path.dirname(os.path.dirname(__file__))

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(base_path, 'openapi.json')
```
