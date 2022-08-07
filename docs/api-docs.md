# API documentation

APIFlask provides support to the following API documentation UIs:

- [Swagger UI](https://github.com/swagger-api/swagger-ui)
- [Redoc](https://github.com/Redocly/redoc)
- [Elements](https://github.com/stoplightio/elements)
- [RapiDoc](https://github.com/rapi-doc/RapiDoc)
- [RapiPDF](https://github.com/mrin9/RapiPdf)


## Change the documentation UI library

The docs UI is controlled via the `docs_ui` parameter when creating the APIFlask
instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_ui='redoc')
```

The following values can be used:

- `swagger-ui` (default value)
- `redoc`
- `elements`
- `rapidoc`
- `rapipdf`


## Change the path to API documentation

The default path of API documentation is `/docs`, so it will be available at
<http://localhost:5000/docs> when running on local with the default port. You can
change the path via the `docs_path` parameter when creating the `APIFlask` instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path='/api-docs')
```

The `docs_path` accepts a URL path starts with a slash, so you can
set a prefix like this:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path='/openapi/docs')
```

Now the local URL of the docs will be <http://localhost:5000/openapi/docs>.

You can also set `openapi_blueprint_url_prefix` to add a prefix to all OpenAPI-related paths.

```python
from apiflask import APIFlask

app = APIFlask(__name__, openapi_blueprint_url_prefix='/openapi')
```

Now the paths to docs and spec will be <http://localhost:5000/openapi/docs>
and <http://localhost:5000/openapi/openapi.json>.


## Add custom API documentation

You can easily add support to other API docs or serve the supported docs UI by yourself.

Just create a view to render the docs template, take Redoc as an example:

```python
from apiflask import APIFlask
from flask import render_template

app = APIFlask(__name__)


@app.route('/redoc')
def my_redoc():
    return render_template('/redoc.html')
```

Here is the template `redoc.html`:

```html hl_lines="17"
<!DOCTYPE html>
<html>
  <head>
    <title>My Redoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url="{{ url_for('openapi.spec') }}"></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
```

In the template, we use `{{ url_for('openapi.spec') }}` to get the URL to the OpenAPI spec file.

Now visit <http://localhost:5000/redoc>, you will see your custom Redoc API docs.

In this way, you can serve multiple API docs at the same time, or add auth protect
to the docs view. If you want to use the built-in configuration variable for API docs or
just want to write less code, you can import the API docs template directly from APIFlask:

```python hl_lines="2 10"
from apiflask import APIFlask
from apiflask.ui_templates import redoc_template
from flask import render_template_string

app = APIFlask(__name__)


@app.route('/redoc')
def my_redoc():
    return render_template_string(redoc_template, title='My API', version='1.0')
```


## Disable the API documentation globally

You can set the `docs_path` parameter to `None` to disable the API documentation:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path=None)
```

!!! tip

    If you want to disable the whole OpenAPI support for the application,
    see *[Disable the OpenAPI support](/openapi/#disable-the-openapi-support)*
    for more details.


## Disable the API documentations for specific blueprints

See *[Disable the OpenAPI support for specific blueprints](/openapi/#disable-for-specific-blueprints)* for more details.


## Disable the API documentations for specific view functions

See *[Disable the OpenAPI support for specific view functions](/openapi/#disable-for-specific-view-functions)* for more details.


## Configure API documentations

The following configuration variables can be used to configure API docs:

- `DOCS_FAVICON`
- `REDOC_USE_GOOGLE_FONT`
- `REDOC_CONFIG`
- `SWAGGER_UI_LAYOUT`
- `SWAGGER_UI_CONFIG`
- `SWAGGER_UI_OAUTH_CONFIG`
- `ELEMENTS_LAYOUT`
- `ELEMENTS_CONFIG`
- `RAPIDOC_THEME`
- `RAPIDOC_CONFIG`
- `RAPIPDF_CONFIG`

See *[Configuration](/configuration/#api-documentations)* for the
introduction and examples of these configuration variables.


## Use different CDN server for API documentation resources

Each resource (JavaScript/CSS files) URL has a configuration variable. You can pass
the URL from your preferred CDN server to the corresponding configuration variables:

- `REDOC_STANDALONE_JS`
- `SWAGGER_UI_CSS`
- `SWAGGER_UI_BUNDLE_JS`
- `SWAGGER_UI_STANDALONE_PRESET_JS`
- `RAPIDOC_JS`
- `ELEMENTS_JS`
- `ELEMENTS_CSS`
- `RAPIPDF_JS`

Here is an example:

```py
# Swagger UI
app.config['SWAGGER_UI_CSS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui.min.css'
app.config['SWAGGER_UI_BUNDLE_JS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui-bundle.min.js'
app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui-standalone-preset.min.js'
# Redoc
app.config['REDOC_STANDALONE_JS'] = 'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js'
# Elements
app.config['ELEMENTS_JS'] = 'https://cdn.jsdelivr.net/npm/@stoplight/elements-dev-portal@1.7.4/web-components.min.js'
app.config['ELEMENTS_CSS'] = 'https://cdn.jsdelivr.net/npm/@stoplight/elements-dev-portal@1.7.4/styles.min.css'
# RapiDoc
app.config['RAPIDOC_JS'] = 'https://cdn.jsdelivr.net/npm/rapidoc@9.3.2/dist/rapidoc-min.min.js'
# RapiPDF
app.config['RAPIPDF_JS'] = 'https://cdn.jsdelivr.net/npm/rapipdf@2.2.1/src/rapipdf.min.js'
```

See *[Configuration](/configuration/#api-documentations)* for the
introduction and examples of these configuration variables.


## Serve API documentation from local resources

Like what you need to do in the last section, to use local resources, you can pass
the URL of local static files to the corresponding configuration variables:

- `REDOC_STANDALONE_JS`
- `SWAGGER_UI_CSS`
- `SWAGGER_UI_BUNDLE_JS`
- `SWAGGER_UI_STANDALONE_PRESET_JS`
- `RAPIDOC_JS`
- `ELEMENTS_JS`
- `ELEMENTS_CSS`
- `RAPIPDF_JS`

For local resources, you can pass a relative URL. For example, if you want to host
the Redoc standalone JavaScript file from a local file, follow the following steps:

Manual download file:

- Download the file from [CDN server][_redoc_cdn]{target=_blank}.
- Put the file in your `static` folder, name it as `redoc.standalone.js` or whatever
you want.
- Figure out the relative URL to your js file. If the file sits in the root of the
`static` folder, then the URL will be `/static/redoc.standalone.js`. If you put it
into a subfolder called `js`, then the URL will be `/static/js/redoc.standalone.js`.
- Pass the URL to the corresponding config:
    ```python
    app.config['REDOC_STANDALONE_JS'] = '/static/js/redoc.standalone.js'
    ```

[_redoc_cdn]: https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js

!!! tip
    The `static` part of the URL matches the `static_url_path` argument you passed
    to the `APIFlask` class, defaults to `static`.

Or with npm:

- Initialize the npm in `static` folder with `npm init`.
- Install the file via `npm i redoc` command.
- Pass the URL to the corresponding config:
    ```python
    app.config['REDOC_STANDALONE_JS'] = 'static/node_modules/redoc/bundles/redoc.standalone.js'
    ```

!!! tip

    The resources of Swagger UI can be found at the `dist` folder of release assets at
    [Swagger UI releases page][_swagger_ui_releases]{target=_blank}.

    [_swagger_ui_releases]: https://github.com/swagger-api/swagger-ui/releases
