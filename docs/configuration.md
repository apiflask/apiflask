# Configuration


## Basics

In Flask, the configuration system is built on top of the `app.config` attribute.
It's a dict-like attribute; thus you can operate it as a dict.

This `app.config` attribute will contain the following configuration variables:

- Flask's built-in configuration variables
- Flask extension's built-in configuration variables
- APIFlask's built-in configuration variables
- Your application's configuration variables

Here is a simple example for basic operates:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

# set a config
app.config['DESCRIPTION'] = 'A wonderful API'

# read a config
description = app.config['DESCRIPTION']
```

Since it's dict-like object, you can also read a configuration variable with
a default value via the `app.config.get()` method:

```python
my_name = app.config.get('DESCRIPTION', 'default value')
```

Or update multiple values at once via `app.config.update()` method:

```python
app.config.update(
    'DESCRIPTION'='A wonderful API',
    'FOO'='bar',
    'ITEMS_PER_PAGE'=15
)
```

For a large application, you can store all the configuration variable in a separate
file, for example, a file called `settings.py`:

```python
MY_CONFIG = 'A wonderful API'
FOO = 'bar'
ITEMS_PER_PAGE = 15
```

Now you can set the configuration variables with the `app.config.from_pyfile()` method:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

# set all configs from settings.py
app.config.from_pyfile('settings.py')
```

Read more about configuration management in
*[Configuration Handling][_config]{target:_blank}* in Flask's documentation.

[_config]: https://flask.palletsprojects.com/config/

!!! warning

    All configuration variables should be in uppercase.

!!! tip "Read a config outside of the application context"

    If you want to read a configuration variable outside of the application context,
    you will get an error like: "Working outside of the application context". This
    usually happened when you use an application factory.

    When you use the application factory, you can access the config with
    `current_app.config` in the view function:

    ```python
    from flask import current_app

    @bp.get('/foo')
    def foo():
        bar = current_app.config['BAR']
    ```

    However, when you define a data schema, there isn't an active application
    context, so you can't use `current_app`. In this situation, you can access
    the configration variables from the module you store them:

    ```python hl_lines="3 6"
    from apiflask import Schema

    from .settings import CATEGORIES  # import the configuration variable

    class PetIn(Schema):
        name = String(required=True, validate=Length(0, 10))
        category = String(required=True, validate=OneOf(CATEGORIES))  # use it
    ```

Below are all the built-in configuration variables in APIFlask.


## OpenAPI fields

All the configurations of OpenAPI-related fields will be used when generating the
OpenAPI spec. They will also be rendered by the API documentation.


### OPENAPI_VERSION

The version of OpenAPI Specification (`openapi.openapi`). This configuration can also
be configured from the `app.openapi_version` attribute.

- Type: `str`
- Default value: `'3.0.3'`
- Examples:

```python
app.config['OPENAPI_VERSION'] = '3.0.2'
```

Or:

```python
app.openapi_version = '3.0.2'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).


### SERVERS

The server information of the API (`openapi.servers`), accepts multiple
server dicts. This configuration can also be configured from the `app.servers`
attribute.

- Type: `List[Dict[str, str]]`
- Default value: `None`
- Examples:

```python
app.config['SERVERS'] = [
    {
        'name': 'Production Server',
        'url': 'http://api.example.com'
    }
]
```

Or:

```python
app.servers = [
    {
        'name': 'Production Server',
        'url': 'http://api.example.com'
    }
]
```


### TAGS

The tag list of the OpenAPI spec documentation (`openapi.tags`), accepts a
list of dicts. You can also pass a simple list contains the tag name string.
This configuration can also be configured from the `app.tags` attribute.

If not set, the blueprint names will use as tags, all the endpoints under the
blueprint will be marked with the blueprint tag automatically.

- Type: `Union[List[str], List[Dict[str, str]]]`
- Default value: `None`
- Examples:

Simple tag name list example:

```python
app.config['TAGS'] = ['foo', 'bar', 'baz']
```

With tag description:

```python
app.config['TAGS'] = [
    {'name': 'foo', 'description': 'The description of foo'},
    {'name': 'bar', 'description': 'The description of bar'},
    {'name': 'baz', 'description': 'The description of baz'}
]
```

Full OpenAPI tags example:

```python
app.config['TAGS'] = [
    {
        'name': 'foo',
        'description': 'tag description',
        'externalDocs': {
            'description': 'Find more info here',
            'url': 'http://example.com'
        }
    }
]
```

Use attribute `app.tags`:

```python
app.tags = ['foo', 'bar', 'baz']
```


### EXTERNAL_DOCS

The external documentation information of the API (`openapi.externalDocs`).
This configuration can also be configured from the `app.external_docs` attribute.

- Type: `Dict[str, str]`
- Default value: `None`
- Examples:

```python
app.config['EXTERNAL_DOCS'] = {
    'description': 'Find more info here',
    'url': 'http://docs.example.com'
}
```

Or:

```python
app.external_docs = {
    'description': 'Find more info here',
    'url': 'http://docs.example.com'
}
```


### INFO

The info field of the API (`openapi.info`). This configuration can also be configured
from the `app.info` attribute. The info object (openapi.info), it accepts a dict contains
following info fields: `description`, `termsOfService`, `contact`, `license`. You can use
separate configuration variables to overwrite this dict.

- Type: `Dict[str, str]`
- Default value: `None`
- Examples:

```python
app.config['INFO'] = {
    'description': '...',
    'termsOfService': 'http://example.com',
    'contact': {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    },
    'license': {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
}
```

Or:

```python
app.info = {
    'description': '...',
    'termsOfService': 'http://example.com',
    'contact': {
        'name': 'API Support',
        'url': 'http://www.example.com/support',
        'email': 'support@example.com'
    },
    'license': {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    }
}
```


### DESCRIPTION

The description of the API (`openapi.info.description`). This configuration can also
be configured from the `app.description` attribute.

- Type: `str`
- Default value: `None`
- Examples:

```python
app.config['DESCRIPTION'] = 'Some description of my API.'
```

Or:

```python
app.description = 'Some description of my API.'
```


### TERMS_OF_SERVICE

The terms of service URL of the API (`openapi.info.termsOfService`).
This configuration can also be configured from the `app.terms_of_service` attribute.

- Type: `str`
- Default value: `None`
- Examples:

```python
app.config['TERMS_OF_SERVICE'] = 'http://example.com/terms/'
```

Or:

```python
app.terms_of_service = 'http://example.com/terms/'
```


### CONTACT

The contact information of the API (`openapi.info.contact`).
This configuration can also be configured from the `app.contact` attribute.

- Type: `Dict[str, str]`
- Default value: `None`
- Examples:

```python
app.config['CONTACT'] = {
    'name': 'API Support',
    'url': 'http://example.com',
    'email': 'support@example.com'
}
```

Or:

```python
app.contact = {
    'name': 'API Support',
    'url': 'http://example.com',
    'email': 'support@example.com'
}
```


### LICENSE

The license of the API (`openapi.info.license`).
This configuration can also be configured from the `app.license` attribute.

- Type: `Dict[str, str]`
- Default value: `None`
- Examples:

```python
app.config['LICENSE'] = {
    'name': 'Apache 2.0',
    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
}
```

Or:

```python
app.license = {
    'name': 'Apache 2.0',
    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
}
```


## OpenAPI spec

Customize the generation of the OpenAPI spec.


### SPEC_FORMAT

The format of the OpenAPI spec, accepts `'json'`, `'yaml'` or `'yml'`. This config
will be used in the following conditions:

- Serve the spec via the built-in route.
- Execute `flask spec` without passing the `--format`/`-f` option.

!!! warning
    The auto-detection of the format from the `APIFlask(spec_path=...)` was
    removed in favor of this config in 0.7.0.

- Type: `str`
- Default value: `'json'`
- Examples:

```python
app.config['SPEC_FORMAT'] = 'yaml'
```

!!! warning "Version >= 0.7.0"

    This configuration variable was added in the [version 0.7.0](/changelog/#version-070).


### LOCAL_SPEC_PATH

The path to the local OpenAPI spec file.

- Type: `str`
- Default value: `None`
- Examples:

```python
app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
```

!!! warning

    If the path you passed is relative, do not put a leading slash in it.

!!! warning "Version >= 0.7.0"

    This configuration variable was added in the [version 0.7.0](/changelog/#version-070).


### LOCAL_SPEC_JSON_INDENT

The indentation of the local OpenAPI spec in JSON format.

- Type: `int`
- Default value: `2`
- Examples:

```python
app.config['LOCAL_SPEC_JSON_INDENT'] = 4
```

!!! warning "Version >= 0.7.0"

    This configuration variable was added in the [version 0.7.0](/changelog/#version-070).


### SYNC_LOCAL_SPEC

If `True`, the local spec will be in sync automatically, see the example usage at
[Keep the local spec in sync automatically](/openapi#keep-the-local-spec-in-sync-automatically).

- Type: `bool`
- Default value: `None`
- Examples:

```python
app.config['SYNC_LOCAL_SPEC'] = True
```

!!! warning "Version >= 0.7.0"

    This configuration variable was added in the [version 0.7.0](/changelog/#version-070).


### JSON_SPEC_MIMETYPE

The MIME type string for JSON OpenAPI spec response.

- Type: `str`
- Default value: `'application/json'`
- Examples:

```python
app.config['JSON_SPEC_MIMETYPE'] = 'application/custom-json'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).


### YAML_SPEC_MIMETYPE

The MIME type string for YAML OpenAPI spec response.

- Type: `str`
- Default value: `'text/vnd.yaml'`
- Examples:

```python
app.config['YAML_SPEC_MIMETYPE'] = 'text/x-yaml'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).


## Automation behavior control

The following configuration variables are used to control the automation behavior
of APIFlask. The default values of all these configuration variables are `True`,
you can disable them if you needed.


### AUTO_TAGS

Enable or disable auto tags (`openapi.tags`) generation from the name of the blueprint.

!!! tip

    This automation behavior only happens when `app.tags` or config `TAGS` is not set.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_TAGS'] = False
```


### AUTO_OPERATION_SUMMARY

Enable or disable auto path summary from the name or docstring of the view function.

!!! tip

    This automation behavior only happens when the view function doesn't decorate
    with `@app.doc(summary=...)`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_OPERATION_SUMMARY'] = False
```

!!! warning

    This variable was renamed from `AUTO_PATH_SUMMARY` to `AUTO_OPERATION_SUMMARY`
    since version 0.8.0.


### AUTO_OPERATION_DESCRIPTION

Enable or disable auto path description from the docstring of the view function.

!!! tip

    This automation behavior only happens when the view function doesn't decorate
    with `@app.doc(description=...)`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_OPERATION_DESCRIPTION'] = False
```

!!! warning

    This variable was renamed from `AUTO_PATH_DESCRIPTION` to `AUTO_OPERATION_DESCRIPTION`
    since version 0.8.0.


### AUTO_OPERATION_ID

!!! warning "Version >= 0.10.0"

    This feature was added in the [version 0.10.0](/changelog/#version-0100).

Enable or disable auto operationId from the method and endpoint of the view function.
See more details in [Set `operationId`](/openapi/#set-operationid).

- Type: `bool`
- Default value: `False`
- Examples:

```python
app.config['AUTO_OPERATION_ID'] = True
```


### AUTO_200_RESPONSE

If a view function doesn't decorate with either `@app.input`, `@app.output`, `@app.auth_required`
or `@app.doc`, APIFlask will add a default 200 response for this view into OpenAPI spec.
Set this config to `False` to disable this behavior.

!!! tip

    You can change the description of the default 200 response with config
    `SUCCESS_DESCRIPTION`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_200_RESPONSE'] = False
```


### `AUTO_404_RESPONSE`

If a view function's URL rule contains a variable. By default, APIFlask will add a
404 response for this view into OpenAPI spec. Set this config to `False` to disable
this behavior.

!!! tip

    You can change the description of the automatic 404 response with config
    `NOT_FOUND_DESCRIPTION`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_404_RESPONSE'] = False
```

!!! warning "Version >= 0.8.0"

    This configuration variable was added in the [version 0.8.0](/changelog/#version-080).


### AUTO_VALIDATION_ERROR_RESPONSE

If a view function uses `@app.input` to validate input request data, APIFlask will add a
validation error response into OpenAPI spec for this view. Set this config to `False`
to disable this behavior.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_VALIDATION_ERROR_RESPONSE'] = False
```


### AUTO_AUTH_ERROR_RESPONSE

If a view function uses `@app.auth_required` to restrict the access, APIFlask will add
an authentication error response into OpenAPI spec for this view. Set this
config to `False` to disable this behavior.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_AUTH_ERROR_RESPONSE'] = False
```


## Response customization

The following configuration variables are used to customize auto-responses.


### SUCCESS_DESCRIPTION

The default OpenAPI description of the 2XX responses.

- Type: `str`
- Default value: `Successful response`
- Examples:

```python
app.config['SUCCESS_DESCRIPTION'] = 'Success!'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).


### NOT_FOUND_DESCRIPTION

The default OpenAPI description of the 404 response.

- Type: `str`
- Default value: `Not found`
- Examples:

```python
app.config['NOT_FOUND_DESCRIPTION'] = 'Missing'
```

!!! warning "Version >= 0.8.0"

    This configuration variable was added in the [version 0.8.0](/changelog/#version-080).


### VALIDATION_ERROR_STATUS_CODE

The status code of validation error response.

- Type: `int`
- Default value: `422`
- Examples:

```python
app.config['VALIDATION_ERROR_STATUS_CODE'] = 422
```


### VALIDATION_ERROR_DESCRIPTION

The OpenAPI description of validation error response.

- Type: `str`
- Default value: `'Validation error'`
- Examples:

```python
app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Invalid JSON body'
```


### VALIDATION_ERROR_SCHEMA

The schema of validation error response, accepts a schema class or
a dict of OpenAPI schema definition.

- Type: `Union[Schema, dict]`
- Default value: `apiflask.schemas.validation_error_schema`
- Examples:

```python
app.config['VALIDATION_ERROR_SCHEMA'] = CustomValidationErrorSchema
```


### AUTH_ERROR_STATUS_CODE

The status code of authentication error response.

- Type: `int`
- Default value: `401`
- Examples:

```python
app.config['AUTH_ERROR_STATUS_CODE'] = 403
```


### AUTH_ERROR_DESCRIPTION

The OpenAPI description of authentication error response.

- Type: `str`
- Default value: `'Authentication error'`
- Examples:

```python
app.config['AUTH_ERROR_DESCRIPTION'] = 'Auth error'
```


### HTTP_ERROR_SCHEMA

The schema of generic HTTP error response, accepts a schema class or
a dict of OpenAPI schema definition.

- Type: `Union[Schema, dict]`
- Default value: `apiflask.schemas.http_error_schema`
- Examples:

```python
app.config['HTTP_ERROR_SCHEMA'] = CustomHTTPErrorSchema
```


### BASE_RESPONSE_SCHEMA

The schema of base response schema, accepts a schema class or a dict of
OpenAPI schema definition.

- Type: `Union[Schema, dict]`
- Default value: `None`
- Examples:

```python
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field

app = APIFlask(__name__)

class BaseResponse(Schema):
    message = String()
    status_code = Integer()
    data = Field()

app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse
```

!!! warning "Version >= 0.9.0"

    This configuration variable was added in the [version 0.9.0](/changelog/#version-090).


### BASE_RESPONSE_DATA_KEY

The data key of the base response, it should match the data field name in the base
response schema.

- Type: `str`
- Default value: `'data'`
- Examples:

```python
app.config['BASE_RESPONSE_DATA_KEY'] = 'data'
```

!!! warning "Version >= 0.9.0"

    This configuration variable was added in the [version 0.9.0](/changelog/#version-090).


## API documentation

The following configuration variables used to customize API documentation.


### DOCS_FAVICON

The absolute or relative URL of the favicon image file of API documentations.

- Type: `str`
- Default value: `'https://apiflask.com/_assets/favicon.png'`
- Examples:

```python
app.config['DOCS_FAVICON'] = 'https://cdn.example.com/favicon.png'
```


### REDOC_USE_GOOGLE_FONT

Enable or disable Google font in Redoc documentation.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['REDOC_USE_GOOGLE_FONT'] = False
```


### REDOC_CONFIG

The configuration options pass to Redoc. See the available options in the
[Redoc documentation](https://github.com/Redocly/redoc#redoc-options-object).

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['REDOC_CONFIG'] = {'disableSearch': True, 'hideLoading': True}
```

!!! warning "Version >= 0.9.0"

    This configuration variable was added in the [version 0.9.0](/changelog/#version-090).


### REDOC_STANDALONE_JS`

The absolute or relative URL of the Redoc standalone JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'`
- Examples:

```python
app.config['REDOC_STANDALONE_JS'] = 'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js'
```


### SWAGGER_UI_CSS

The absolute or relative URL of the Swagger UI CSS file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'`
- Examples:

```python
app.config['SWAGGER_UI_CSS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui.min.css'
```


### SWAGGER_UI_BUNDLE_JS

The absolute or relative URL of the Swagger UI bundle JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js'`
- Examples:

```python
app.config['SWAGGER_UI_BUNDLE_JS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui-bundle.min.js'
```


### SWAGGER_UI_STANDALONE_PRESET_JS

The absolute or relative URL of the Swagger UI standalone preset JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js'`
- Examples:

```python
app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui-standalone-preset.min.js'
```


### SWAGGER_UI_LAYOUT

The layout of Swagger UI, one of `'BaseLayout'` and `'StandaloneLayout'`.

- Type: `str`
- Default value: `'BaseLayout'`
- Examples:

```python
app.config['SWAGGER_UI_LAYOUT'] = 'StandaloneLayout'
```


### SWAGGER_UI_CONFIG

The config for Swagger UI, these config values will overwrite the existing config,
such as `SWAGGER_UI_LAYOUT`.

!!! tip

    See *[Configuration][_swagger_conf]{target=_blank}* of the Swagger UI docs
    for available config options.

[_swagger_conf]: https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['SWAGGER_UI_CONFIG'] = {
    'layout': 'StandaloneLayout'
}
```


### SWAGGER_UI_OAUTH_CONFIG

The config for Swagger UI OAuth:

```js
ui.initOAuth(yourConfig)
```

!!! tip

    See the *[OAuth 2.0 configuration][_swagger_oauth]{target=_blank}* in Swagger UI
    docs for available config options.

[_swagger_oauth]: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['SWAGGER_UI_OAUTH_CONFIG'] = {
    'realm': 'foo'
}
```


### ELEMENTS_CSS

The absolute or relative URL of the Elements CSS file.

- Type: `str`
- Default value: `'https://unpkg.com/@stoplight/elements/styles.min.css'`
- Examples:

```python
app.config['ELEMENTS_CSS'] = 'https://cdn.jsdelivr.net/npm/@stoplight/elements-dev-portal@1.7.4/styles.min.css'
```


### ELEMENTS_JS

The absolute or relative URL of the Elements JavaScript file.

- Type: `str`
- Default value: `'https://unpkg.com/@stoplight/elements/web-components.min.js'`
- Examples:

```python
app.config['ELEMENTS_JS'] = 'https://cdn.jsdelivr.net/npm/@stoplight/elements-dev-portal@1.7.4/web-components.min.js'
```


### ELEMENTS_LAYOUT

The layout of Elements, one of `'sidebar'` and `'stacked'`.

- Type: `str`
- Default value: `'sidebar'`
- Examples:

```python
app.config['ELEMENTS_LAYOUT'] = 'stacked'
```


### ELEMENTS_CONFIG

The config for Elements, these config values will overwrite the existing config,
such as `ELEMENTS_LAYOUT`.

!!! tip

    See *[Elements Configuration Options][_elements_conf]{target=_blank}*
    for available config options.

[_elements_conf]: https://github.com/stoplightio/elements/blob/main/docs/getting-started/elements/elements-options.md

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['ELEMENTS_CONFIG'] = {
    'hideTryIt': 'true',
    'layout': 'stacked',
}
```


### RAPIDOC_JS

The absolute or relative URL of the RapiDoc JavaScript file.

- Type: `str`
- Default value: `'https://unpkg.com/rapidoc/dist/rapidoc-min.js'`
- Examples:

```python
app.config['RAPIDOC_JS'] = 'https://cdn.jsdelivr.net/npm/rapidoc@9.3.2/dist/rapidoc-min.min.js'
```


### RAPIDOC_THEME

The theme of RapiDoc, one of `'light'` and `'dark'`.

- Type: `str`
- Default value: `'light'`
- Examples:

```python
app.config['RAPIDOC_THEME'] = 'dark'
```


### RAPIDOC_CONFIG

The config for RapiDoc, these config values will overwrite the existing config,
such as `RAPIDOC_THEME`.

!!! tip

    See *[RapiDoc API][_rapidoc_conf]{target=_blank}* of the RapiDoc docs
    for available config options.

[_rapidoc_conf]: https://rapidocweb.com/api.html

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['RAPIDOC_CONFIG'] = {
    'update-route': False,
    'layout': 'row'
}
```


### RAPIPDF_JS

The absolute or relative URL of the RapiPDF JavaScript file.

- Type: `str`
- Default value: `'https://unpkg.com/rapipdf/dist/rapipdf-min.js'`
- Examples:

```python
app.config['RAPIPDF_JS'] = 'https://cdn.jsdelivr.net/npm/rapipdf@2.2.1/src/rapipdf.min.js'
```


### RAPIPDF_CONFIG

The config for RapiPDF.

!!! tip

    See *[RapiPDF API][_rapipdf_conf]{target=_blank}* of the RapiPDF docs
    for available config options.

[_rapipdf_conf]: https://mrin9.github.io/RapiPdf/api.html

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['RAPIPDF_CONFIG'] = {
    'include-example': True,
    'button-label': 'Generate!'
}
```


## Flask built-in configuration variables

See *[Builtin Configuration Values][_flask_config]{target:_blank}* for the
built-in configuration variables provided by Flask.

[_flask_config]: https://flask.palletsprojects.com/config/#builtin-configuration-values
