# APIFlask Change Log

## Version 0.2.0
Released: 2021-3-27

- Fix various bugs.
- Refactor the package and tests (100% coverage).
- Rename most of the APIs.
- Add new APIs:
    - `APIFlask`
    - `APIBlueprint`
    - `HTTPError`
    - `api_json`
    - `HTTPTokenAuth`
    - `HTTPBasicAuth`
    - `@doc`
    - `EmptySchema`
- Add a bunch of new configuration variables:
    - `DESCRIPTION`
    - `TAGS`
    - `CONTACT`
    - `LICENSE`
    - `SERVERS`
    - `EXTERNAL_DOCS`
    - `TERMS_OF_SERVICE`
    - `SPEC_FORMAT`
    - `AUTO_TAGS`
    - `AUTO_DESCRIPTION`
    - `AUTO_PATH_SUMMARY`
    - `AUTO_PATH_DESCRIPTION`
    - `AUTO_200_RESPONSE`
    - `DEFAULT_2XX_DESCRIPTION`
    - `DEFAULT_200_DESCRIPTION`
    - `DEFAULT_201_DESCRIPTION`
    - `DEFAULT_204_DESCRIPTION`
    - `AUTO_VALIDATION_ERROR_RESPONSE`
    - `VALIDATION_ERROR_STATUS_CODE`
    - `VALIDATION_ERROR_DESCRIPTION`
    - `VALIDATION_ERROR_SCHEMA`
    - `AUTO_AUTH_ERROR_RESPONSE`
    - `AUTH_ERROR_STATUS_CODE`
    - `AUTH_ERROR_DESCRIPTION`
    - `AUTH_ERROR_SCHEMA`
    - `AUTO_HTTP_ERROR_RESPONSE`
    - `HTTP_ERROR_SCHEMA`
    - `DOCS_HIDE_BLUEPRINTS`
    - `DOCS_FAVICON`
    - `REDOC_USE_GOOGLE_FONT`
    - `REDOC_STANDALONE_JS`
    - `SWAGGER_UI_CSS`
    - `SWAGGER_UI_BUNDLE_JS`
    - `SWAGGER_UI_STANDALONE_PRESET_JS`
    - `SWAGGER_UI_LAYOUT`
    - `SWAGGER_UI_CONFIG`
    - `SWAGGER_UI_OAUTH_CONFIG`
- Support to hide blueprint from API docs with config `DOCS_HIDE_BLUEPRINTS` ([commit](https://github.com/greyli/apiflask/commit/3b2cc0097defaabf0b916e00930dda1da8226430))
- Support to deprecate and hide an endpoint with `doc(hide=True, deprecated=True)`([commit](https://github.com/greyli/apiflask/commit/82d181a7080bd4088ee8db929e81431a723cda93))
- Support to customize the API docs with various configuration variables. ([commit](https://github.com/greyli/apiflask/commit/294379428f5032c6c8228841a836a37860012c0f))
- Support to set all fields of OpenAPI object and Info object ([commit](https://github.com/greyli/apiflask/commit/a7990e28e73bdd5b86c1471aa97861025e14295f))
- Support YAML format spec ([commit](https://github.com/greyli/apiflask/commit/ce6975bb465e01b0e48b2b8adce0f99a8db56e01))
- Automatically register a validation error response for endpoints which use `@input`. ([commit](https://github.com/greyli/apiflask/commit/c3d7c3b585ca5d7f9f6d84f16137dd257bfe0518))
- Automatically register a authorization error response for endpoints which use `@auth_required`. ([commit](https://github.com/greyli/apiflask/commit/c8992a8e420522a3e66563e455aa628f0f20a09c))
- Automatically add response schema for responses added with `@doc(responses=...)`. ([commit](https://github.com/greyli/apiflask/commit/1b7dce5f722d038be5dc726d52a0eefd0365eeeb))
- Pass view arguments to view function as positional arguments ([commit](https://github.com/greyli/apiflask/commit/15c66f3ba97310ed10c851721177e6c504a87317))
- Require Python 3.7 to use ordered dict ([commit](https://github.com/greyli/apiflask/commit/557a7e649b64aef8f4b8596a4af175524d108ff4))
- Add shortcuts for `app.route`: `app.get()`, `app.post()`, etc. ([commit](https://github.com/greyli/apiflask/commit/48bc1246628e53573c811def4a909be0faa9dcfb))
- Not an extension any more ([commit](https://github.com/greyli/apiflask/commit/ecaec37544524deb8b2ce445d4a3cbf990ff95cb))

## Version 0.1.0
Released: 2021-1-27

- Add view functions without response schema into spec ([commit](https://github.com/greyli/apiflask/commit/aabf427590227001e0e443d8d6a3bf5f56dc5964))       
- Set default response descriptions ([commit](https://github.com/greyli/apiflask/commit/b9edf9e8f5731a8f45b359f6a101b4d39ba3f2f5))
- Stop rely on Flask-Marshmallow ([commit](https://github.com/greyli/apiflask/commit/cce7a0b8b97f345e087973b127c6d25c884dbc8f))
- Change default spec path to `openapi.json` ([commit](https://github.com/greyli/apiflask/commit/09d0d278a1fc27fa5868ef5848f3931bd8f76ef4))
- Add support for enabling Swagger UI and Redoc at the same time ([commit](https://github.com/greyli/apiflask/commit/d5176418b8c22e523d8b82e1f9af8f2403fa70bb))
- Change default spec title and version ([commit](https://github.com/greyli/apiflask/commit/0953c310327539f96bcdfad142772c7800285d56))
- Support auto generating summary from function name ([commit](https://github.com/greyli/apiflask/commit/d3d7cc2f63f3cf26466e42d68a03b4d96bf2fd97))
- Start as a fork of [APIFairy 0.6.2](https://github.com/miguelgrinberg/APIFairy/releases/tag/v0.6.2) at 2021-01-13.
