# Swagger UI and Redoc


## Change the path to Swagger UI and Redoc

The default path of Swagger UI is `/docs`, so it will be available at
<http://localhost:5000/docs> when running on local with the default port. You can
change the path via the `docs_path` parameter when creating the `APIFlask` instance:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path='/swagger-ui')
```

Similarly, the default path of Redoc is `/redoc`, and you can change it via the
`redoc_path` parameter:

```python
from apiflask import APIFlask

app = APIFlask(__name__, redoc_path='/api-doc')
```

The `docs_path` and `redoc_path` accepts a URL path starts with a slash, so you can
set a prefix like this:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path='/docs/swagger-ui', redoc_path='/docs/redoc')
```

Now the local URL of the docs will be <http://localhost:5000/docs/swagger-ui> and
<http://localhost:5000/docs/redoc>.


## Disable the API documentations globally

You can set the `docs_path` parameter to `None` to disable Swagger UI documentation:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path=None)
```

Similarly, you can set the `redoc_path` parameter to `None` to disable Redoc
documentation:

```python
from apiflask import APIFlask

app = APIFlask(__name__, redoc_path=None)
```

Or disable both:

```python
from apiflask import APIFlask

app = APIFlask(__name__, docs_path=None, redoc_path=None)
```

!!! tip

    If you want to disable the whole OpenAPI support for the application, you
    can set `enable_openapi` parameter to `False` when creating the `APIFlask` instance:

    ```python
    from apiflask import APIFlask

    app = APIFlask(__name__, enable_openapi=False)
    ```


## Disable the API documentations for specific blueprints

To hide blueprints from API documentations (and OpenAPI spec), you can
set `enable_openapi` parameter to `False` when creating the `APIBlueprint` instance:

```python
from apiflask import APIBlueprint

bp = APIBlueprint(__name__, 'foo', enable_openapi=False)
```


## Disable the API documentations for specific view functions

To hide a view function from API documentations (and OpenAPI spec), you
can set the `hide` parameter to `True` in the `@doc` decorator:

```python hl_lines="1 4"
from apiflask import doc

@app.get('/secret')
@doc(hide=True)
def some_secret():
    return ''
```

!!! note

    By default, APIFlask will add a view function into API documentations
    (and OpenAPI spec) even if the view function doesn't use `@input`, `@output`,
    and `@doc` decorator. If you want to disable this behavior, set configruration
    variable `AUTO_200_RESPONSE` to `False`:

    ```python
    app.config['AUTO_200_RESPONSE'] = False
    ```


## Configure Swagger UI/Redoc

The following configuration variables can be used to config Swagger UI/Redoc:

- `DOCS_FAVICON`
- `REDOC_USE_GOOGLE_FONT`
- `SWAGGER_UI_LAYOUT`
- `SWAGGER_UI_CONFIG`
- `SWAGGER_UI_OAUTH_CONFIG`

See *[Configuration](/configuration/#swagger-ui-and-redoc)* for the
introduction and examples of these configuration variables.


## Use different CND server for Swagger UI/Redoc resources

Each resource (JavaScript/CSS files) URL has a configuration variable. You can pass
the URL from your preferred CND server to the corresponding configuration variables:

- `REDOC_STANDALONE_JS`
- `SWAGGER_UI_CSS`
- `SWAGGER_UI_BUNDLE_JS`
- `SWAGGER_UI_STANDALONE_PRESET_JS`

See *[Configuration](/configuration/#swagger-ui-and-redoc)* for the
introduction and examples of these configuration variables.


## Serve Swagger UI/Redoc from local resources

Like what you need to do in the last section, to use local resources, you can pass
the URL of local static files to the corresponding configuration variables:

- `REDOC_STANDALONE_JS`
- `SWAGGER_UI_CSS`
- `SWAGGER_UI_BUNDLE_JS`
- `SWAGGER_UI_STANDALONE_PRESET_JS`

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

[_redoc_cdn]: https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js

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
