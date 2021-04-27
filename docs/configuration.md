# Configuration

## Basics

In Flask, conguration system is built on top the `app.config` attribute. It's dict-like attribute, thus you can operate it as a dict.

This `app.config` attribute will contains the following configuration variables:

- Flask's built in configuration variables
- Flask extension's built in configuration variables
- APIFlask's built in configuration variables
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

Since it's dict-like object, you can also read a config wth a default value via
`app.config.get()` method:

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

For a large application, you may want to store all configs in an seprate file,
for example, a file called `settings.py`:

```python
MY_CONFIG = 'A wonderful API'
FOO = 'bar'
ITEMS_PER_PAGE = 15
```

Now you can set the configuration variables with `app.config.from_pyfile()` method:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

# set all configs from settings.py
app.config.from_pyfile('settings.py')
```

Read more about configuration mangament in the "[Configuration Handling][_config]" chapter
of Flask's documentation.

[_config]: https://flask.palletsprojects.com/config/

!!! warning
    All configuration variable should in uppercase.

!!! tip "Reading a config outside of the application context"

    If you want to read a configuration variable outside of the application context,
    you will get some error like: "Working outside of the application context". The
    usually happened when you use application factory.

    When you use application factory, you can access the config with `current_app.config` in the view function:

    ```python
    from flask import current_app

    @bp.get('/foo')
    def foo():
        bar = current_app.config['BAR']
    ```

    However, when you define a resource schema, there isn't a application context exists, you can't use `current_app`. In this situation, you can just access the configration
    variables from the module you store them:

    ```python hl_lines="3 6"
    from apiflask import Schema

    from .settings import CATEGORIES  # import the configuration variable

    class PetInSchema(Schema):
        name = String(required=True, validate=Length(0, 10))
        category = String(required=True, validate=OneOf(CATEGORIES))  # use it
    ```

## Built-in configuration variables

Below are all the built-in configuration variables in APIFlask.

### OpenAPI fields

All the configurations of OpenAPI-related fields will be used when the OpenAPI spec was
generated. They will also rendered by the API documentations.

#### `OPENAPI_VERSION`

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

#### `DESCRIPTION`

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

#### `TAGS`

The tags of the OpenAPI spec documentation (`openapi.tags`), accepts a
list of dicts. You can also pass a simple list contains the tag names.
This configuration can also be configured from the `app.tags` attribute.

If not set, the blueprint names will be used as tags, each views under the
blueprint will marked with the blueprint tag automatically.

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

#### `CONTACT`

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

#### `LICENSE`

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

#### `SERVERS`

The servers information of the API (`openapi.servers`), accepts multiple
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

#### `EXTERNAL_DOCS`

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

#### `TERMS_OF_SERVICE`

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

#### `JSON_SPEC_MIMETYPE`

The MIME type string for JSON OpenAPI spec response.

- Type: `str`
- Default value: `'application/json'`
- Examples:

```python
app.config['JSON_SPEC_MIMETYPE'] = 'application/custom-json'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).

#### `YAML_SPEC_MIMETYPE`

The MIME type string for YAML OpenAPI spec response.

- Type: `str`
- Default value: `'text/vnd.yaml'`
- Examples:

```python
app.config['YAML_SPEC_MIMETYPE'] = 'text/x-yaml'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).

### Automation behaviour control

The following configuration variables used to control the automation behaviour of APIFlask.
The default values of all these configuration variables are `True`, you can disable them
when you needed.

#### `AUTO_TAGS`

Enable or disable auto tags (`openapi.tags`) generation from the name of blueprint.

!!! tip
    This automation behaviour only happens when `app.tags` or config `TAGS` is not set.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_TAGS'] = False
```

#### `AUTO_PATH_SUMMARY`

Enable or disable auto path summary from the name or docstring of the view function.

!!! tip
    This automation behaviour only happens when the view function doesn't decorated
    with `@doc(summary=...)`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_PATH_SUMMARY'] = False
```

#### `AUTO_PATH_DESCRIPTION`

Enable or disable auto path description from the docstring of the view function.

!!! tip
    This automation behaviour only happens when the view function doesn't decorated
    with `@doc(description=...)`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_PATH_DESCRIPTION'] = False
```

#### `AUTO_200_RESPONSE`

If a view function doesn't decorated with either `@input`, `@output`, `@auth_required`
or `@doc`. By default, APIFlask will add an default 200 response for this view into OpenAPI
spec. Set this config to `False` to disable this behaviour.

!!! tip
    You can change the description of the default 200 response with config
    `DEFAULT_200_DESCRIPTION`.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_200_RESPONSE'] = False
```

#### `AUTO_VALIDATION_ERROR_RESPONSE`

If a view function use `@input` to validate input request data, APIFlask will add a
validation error response into OpenAPI spec for this view. Set this config to `False`
to disable this behaviour.
 
- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_VALIDATION_ERROR_RESPONSE'] = False
```

#### `AUTO_AUTH_ERROR_RESPONSE`

If a view function use `@auth_required` to restrict the access, APIFlask will add a
authentication error response into OpenAPI spec for this view. Set this config to `False`
to disable this behaviour.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['AUTO_AUTH_ERROR_RESPONSE'] = False
```

### Response customization

The following configuration variables used to customize auto responses.

#### `SUCCESS_DESCRIPTION`

The default description of the 2XX responses.

- Type: `str`
- Default value: `Successful response`
- Examples:

```python
app.config['SUCCESS_DESCRIPTION'] = 'Success!'
```

!!! warning "Version >= 0.4.0"

    This configuration variable was added in the [version 0.4.0](/changelog/#version-040).

#### `VALIDATION_ERROR_STATUS_CODE`

The status code of validation error response.

- Type: `int`
- Default value: `400`
- Examples:

```python
app.config['VALIDATION_ERROR_STATUS_CODE'] = 422
```

#### `VALIDATION_ERROR_DESCRIPTION`

The description of validation error response.

- Type: `str`
- Default value: `'Validation error'`
- Examples:

```python
app.config['VALIDATION_ERROR_DESCRIPTION'] = 'Invalid JSON body'
```

#### `VALIDATION_ERROR_SCHEMA`

The schema of validation error response, accepts a schema class or
a dict of OpenAPI schema definition.

- Type: `Union[Schema, dict]`
- Default value: `apiflask.schemas.validation_error_schema`
- Examples:

```python
app.config['VALIDATION_ERROR_SCHEMA'] = CustomValidationErrorSchema
```

#### `AUTH_ERROR_STATUS_CODE`

The status code of authentication error response.

- Type: `int`
- Default value: `401`
- Examples:

```python
app.config['AUTH_ERROR_STATUS_CODE'] = 403
```

#### `AUTH_ERROR_DESCRIPTION`

The description of authentication error response.

- Type: `str`
- Default value: `'Authentication error'`
- Examples:

```python
app.config['AUTH_ERROR_DESCRIPTION'] = 'Auth error'
```

#### `HTTP_ERROR_SCHEMA`

The schema of generic HTTP error response, accepts a schema class or
a dict of OpenAPI schema definition.

- Type: `Union[Schema, dict]`
- Default value: `'Empty response'`
- Examples:

```python
app.config['HTTP_ERROR_SCHEMA'] = CustomHTTPErrorSchema
```

### Swagger UI and Redoc

The following configuration variables used to customize Swagger UI and
Redoc documentation.

#### `DOCS_FAVICON`

The absolute or relative URL of the favicon image file of API documentations.

- Type: `str`
- Default value: `None`
- Examples:

```python
app.config['DOCS_FAVICON'] = 'https://cdn.example.com/favicon.png'
```

#### `REDOC_USE_GOOGLE_FONT`

Enable or disable Google font in Redoc documentation.

- Type: `bool`
- Default value: `True`
- Examples:

```python
app.config['REDOC_USE_GOOGLE_FONT'] = False
```

#### `REDOC_STANDALONE_JS`

The absolute or relative URL of the Redoc standalone JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'`
- Examples:

```python
app.config['REDOC_STANDALONE_JS'] = 'https://cdn.example.com/filename.js'
```

#### `SWAGGER_UI_CSS`

The absolute or relative URL of the Swagger UI CSS file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'`
- Examples:

```python
app.config['SWAGGER_UI_CSS'] = 'https://cdn.example.com/filename.js'
```

#### `SWAGGER_UI_BUNDLE_JS`

The absolute or relative URL of the Swagger UI bundle JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js'`
- Examples:

```python
app.config['SWAGGER_UI_BUNDLE_JS'] = 'https://cdn.example.com/filename.js'
```

#### `SWAGGER_UI_STANDALONE_PRESET_JS`

The absolute or relative URL of the Swagger UI standalone preset JavaScript file.

- Type: `str`
- Default value: `'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js'`
- Examples:

```python
app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = 'https://cdn.example.com/filename.js'
```

#### `SWAGGER_UI_LAYOUT`

The layout of Swagger UI, one of `'BaseLayout'` and `'StandaloneLayout'`.

- Type: `str`
- Default value: `'BaseLayout'`
- Examples:

```python
app.config['SWAGGER_UI_LAYOUT'] = 'StandaloneLayout'
```

#### `SWAGGER_UI_CONFIG`

The config for Swagger UI, this config value will overwrite the existing config such
as `SWAGGER_UI_LAYOUT`.

!!! tip
    See the [Configuration][_swagger_configuration] chapter of the Swagger UI docs for more details.

[_swagger_configuration]: https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['SWAGGER_UI_CONFIG'] = {
    'layout': 'StandaloneLayout'
}
```

#### `SWAGGER_UI_OAUTH_CONFIG`

The config for Swagger UI OAuth:

```js
ui.initOAuth(yourConfig)
```

!!! tip
    See the [OAuth 2.0 configuration][_swagger_oauth] chapter of the Swagger UI docs for more details.

[_swagger_oauth]: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/

- Type: `dict`
- Default value: `None`
- Examples:

```python
app.config['SWAGGER_UI_OAUTH_CONFIG'] = {
    'realm': 'foo'
}
```

## Flask built-in configuration variables

See [Flask's documentation](_flask_config) for the built-in configuration variables provided by Flask.

[_flask_config]: https://flask.palletsprojects.com/config/#builtin-configuration-values
