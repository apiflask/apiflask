## Versions 1.2.0

- [1.2.0 milestone](https://github.com/apiflask/apiflask/milestone/12)
- [1.2.0 kanban](https://github.com/apiflask/apiflask/projects/3)

Released: -


## Version 1.1.1

Released: 2022/8/3

- Improve CI setup and test again Python 3.10 and 3.11.
- Fix the typing of `APIFlask` path parameters ([issue #329][issue_329]).
- Update `MethodViewType` usages for Flask 2.2 ([issue #335][issue_335]).

[issue_329]: https://github.com/apiflask/apiflask/issues/329
[issue_335]: https://github.com/apiflask/apiflask/issues/335


## Version 1.1.0

Released: 2022/7/3

- Add a versioned docs for 1.x releases (https://v1.apiflask.com).
- Allow the view function to return a list as JSON response ([issue #321][issue_321]).
- Add new docs UI support: RapiDoc, RapiPDF, and Elements ([pr #308][pr_308]).
- Add a `docs_ui` parameter to APIFlask to set the API docs UI (can be
  `swagger-ui` (default), `redoc`, `rapidoc`, and `rapipdf`).
- Deprecate the separate docs path `/redoc` and the `redoc_path` parameter.
- Add the following configuration variables for new docs supprt:
    - `ELEMENTS_JS`
    - `ELEMENTS_CSS`
    - `ELEMENTS_LAYOUT`
    - `ELEMENTS_CONFIG`
    - `RAPIDOC_JS`
    - `RAPIDOC_THEME`
    - `RAPIDOC_CONFIG`
    - `RAPIPDF_JS`
    - `RAPIPDF_CONFIG`
- Fix CLI entry point setup to prevent overwriting `flask`
  ([issue #312][issue_312])

[pr_308]: https://github.com/apiflask/apiflask/pull/308
[issue_312]: https://github.com/apiflask/apiflask/issues/312
[issue_321]: https://github.com/apiflask/apiflask/issues/321


## Version 1.0.2

Released: 2022/5/21

- Combine custom security schemes (app.security_schemes) with existing values
  ([issue #293][issue_293]).
- Add the missing `path` (`view_args`) to the valid request `location` list
  ([issue #301][issue_301])
- Fix the security scheme values to lowercase.

[issue_293]: https://github.com/apiflask/apiflask/issues/293
[issue_301]: https://github.com/apiflask/apiflask/issues/301


## Version 1.0.1

Released: 2022/5/17

- Fix the async support for `app.auth_required`, `app.input`, and `app.doc` decorators
  ([issue #288][issue_288]). Thanks [@jiashuChen](https://github.com/jiashuChen)!

[issue_288]: https://github.com/apiflask/apiflask/issues/288


## Version 1.0.0

Released: 2022/5/4<br>Codename: Wujiaochang

- Remove the deprecated standalone decorators: `input`, `output`, `doc`, and `auth_required`.
  Use app/blueprint decorators instead (e.g. `input()` -> `app.input()`/`bp.input()`).
- Deprecate the following parameters ([issue #237][issue_237]):
    - `role` in `app.auth_required()`/`bp.auth_required()`, use `roles` and always pass a list.
    - `tag` in `app.doc()`/`bp.doc()`, use `tags` and always pass a list.
- Add a base class (`apiflask.scaffold.APIScaffold`) for common logic of `APIFlask` and
  `APIBlueprint`, move route decorators and API-related decorators to this base class
  to improve the IDE auto-completion ([issue #231][issue_231]).
- Support customizing OpenAPI securitySchemes and operation security, this makes it
  possible to use any external authentication libraries ([pull #232][pull_232]).
- Improve the way to detect blueprint from view endpoint to support the endpoints that
  contain dots ([issue #211][issue_211]).
- Support file uploading ([issue #123][issue_123]):
    - Fix the content type of `form` and `files` input locations.
    - Raise error if the user uses multiple body input locations ("files", "form", "json").
    - Add `Form` field and `form_and_files` location for better form upload support.
    - Rewrite the `files` to act like `form_and_files`, so that failed parsed file will
      be included in the returned data.
- Allow to use `json_or_form` location and fields (`DelimitedList` and `DelimitedTuple`)
  from webargs ([issue #254][issue_254]).
- When creating a custom error processor, call it for generic HTTP errors even if the
  `json_errors` is set to `False` when creating the app instance ([issue #171][issue_171]).

[issue_211]: https://github.com/apiflask/apiflask/issues/211
[issue_231]: https://github.com/apiflask/apiflask/issues/231
[pull_232]: https://github.com/apiflask/apiflask/pull/232
[issue_237]: https://github.com/apiflask/apiflask/issues/237
[issue_123]: https://github.com/apiflask/apiflask/issues/123
[issue_254]: https://github.com/apiflask/apiflask/issues/254
[issue_171]: https://github.com/apiflask/apiflask/issues/171


## Version 0.12.0

Released: 2022/3/2

- Move standalone decorators (input, output, auth_required, doc) to APIFlask/APIBlueprint
  classes. The old decorators are deprecated and will be removed in 1.0. ([issue #187][issue_187]).

[issue_187]: https://github.com/apiflask/apiflask/issues/187


## Version 0.11.0

Released: 2021/12/6

- Support creating custom error classes based on `HTTPError`. The position argument `status_code` of
  `HTTPError` is changed to a keyword argument, defaults to `500` ([issue #172][issue_172]).

[issue_172]: https://github.com/apiflask/apiflask/issues/172


## Version 0.10.1

Released: 2021/11/26

- Fix missing headers for JSON error responses when catching Werkzeug exceptions ([issue #173][issue_173]).

[issue_173]: https://github.com/apiflask/apiflask/issues/173


## Version 0.10.0

Released: 2021/9/19

- Support using `add_url_rule` method on view classes ([issue #110][issue_110]).
- Revoke the undocumented name changes on `validates` and `validates_schema` from marshmallow ([issue #62][issue_62]).
- Only expose marshmallow `fields`, `validators`, and `Schema` in APIFlask.
- Remove the `status_code` field from the default error response ([issue #124][issue_124]).
- Add parameter `extra_data` to `abort` and `HTTPError`, it accepts a dict that will be added
  to the error response ([issue #125][issue_125]).
- Support passing `operation_id` in the `doc` decorator. The auo-generating of operationId
  can be enabled with config `AUTO_OPERATION_ID`, defaults to `False` ([pull #131][pull_131]).
- Support setting response links via `@output(links=...)` ([issue #138][issue_138]).

[issue_110]: https://github.com/apiflask/apiflask/issues/110
[issue_62]: https://github.com/apiflask/apiflask/issues/62
[issue_124]: https://github.com/apiflask/apiflask/issues/124
[issue_125]: https://github.com/apiflask/apiflask/issues/125
[pull_131]: https://github.com/apiflask/apiflask/pull/131
[issue_138]: https://github.com/apiflask/apiflask/issues/138


## Version 0.9.0

Released: 2021/8/10

- Support base response schema customization, add config `BASE_RESPONSE_SCHEMA`
  and `BASE_RESPONSE_DATA_KEY` ([issue #65][issue_65]).
- Support setting custom schema name resolver via the `APIFlask.schema_name_resolver`
  attribute ([issue #105][issue_105]).
- Improve error handling ([issue #107][issue_107]):
    - Authentication error now calls app error processor function when `APIFlask(json_errors=True)`.
      The default HTTP reason phrase is used for auth errors.
    - Always pass an `HTTPError` instance to error processors. When you set a custom error
      processor, now you need to accept an `HTTPError` instance as the argument. The `detail` and
      `headers` attribute of the instance will be empty dict if not set.
    - Add an `error_processor` decorator for `HTTPTokenAuth` and `HTTPBasicAuth`, it can be used
      to register a custom error processor for auth errors.
- Support to config Redoc via the configuration variable `REDOC_CONFIG` ([issue #121][issue_121]).

[issue_65]: https://github.com/apiflask/apiflask/issues/65
[issue_105]: https://github.com/apiflask/apiflask/issues/105
[issue_107]: https://github.com/apiflask/apiflask/issues/107
[issue_121]: https://github.com/apiflask/apiflask/issues/121


## Version 0.8.0

Released: 2021/7/7

- Automatically add a 404 response in OpenAPI spec for routes contains URL
  variables ([issue #78][issue_78]).
- Rename the private method `app.get_spec` to `app._get_spec`, add new
  parameter `force_update`. The `app.spec` property now will always return
  the latest spec instead of the cached one ([issue #79][issue_79]).
- Support using `doc(responses={<STATUS_CODE>: <DESCRIPTION>})` to overwrite
  existing response descriptions.
- Add configration variable `INFO` (and `app.info` attribute), it can be used
  to set the following info fields: `description`, `termsOfService`, `contact`,
`license` ([issue #98][issue_98]).
- Rename the following configuration variables ([issue #99][issue_99]):
    - `AUTO_PATH_SUMMARY` -> `AUTO_OPERATION_SUMMARY`
    - `AUTO_PATH_DESCRIPTION` -> `AUTO_OPERATION_DESCRIPTION`

[issue_78]: https://github.com/apiflask/apiflask/issues/78
[issue_79]: https://github.com/apiflask/apiflask/issues/79
[issue_98]: https://github.com/apiflask/apiflask/issues/98
[issue_99]: https://github.com/apiflask/apiflask/issues/99


## Version 0.7.0

Released: 2021/6/24

- Support using async error processor and async spec processor
([pull #57][pull_57]).
- Fix auto-tag support for nesting blueprint ([pull #58][pull_58]).
- Support set the URL prefix of the OpenAPI blueprint with the
  `openapi_blueprint_url_prefix` argument ([pull #64][pull_64]).
- Add a `flask spec` command to output the OpenAPI spec to stdout
  or a file, also add new config `LOCAL_SPEC_PATH` and
  `LOCAL_SPEC_JSON_INDENT` ([issue #61][issue_61]).
- Re-add the `SPEC_FORMAT` config. Remove the auto-detection of
  the format from `APIFlask(spec_path=...)`, now you have to set the
  format explicitly with the `SPEC_FORMAT` config ([issue #67][issue_67]).
- Support to sync the local OpenAPI spec automatically. Add new config
  `SYNC_LOCAL_SPEC` ([issue #68][issue_68]).
- Change the default value of config `DOCS_FAVICON` to
  `'https://apiflask.com/_assets/favicon.png'`, set to `None` to disable
  the favicon.
- OpenAPI UI templates are move to `ui_templates.py`.
- Revert the renames on pre/post decorators from marshmallow ([issue #62][issue_62]).
- Change the default branch to "main".
- Move the source to the "src" directory.
- Enable pre-commit.

[pull_57]: https://github.com/apiflask/apiflask/pull/57
[pull_58]: https://github.com/apiflask/apiflask/pull/58
[pull_64]: https://github.com/apiflask/apiflask/pull/64
[issue_61]: https://github.com/apiflask/apiflask/issues/61
[issue_62]: https://github.com/apiflask/apiflask/issues/62
[issue_67]: https://github.com/apiflask/apiflask/issues/67
[issue_68]: https://github.com/apiflask/apiflask/issues/68


## Version 0.6.3

Released: 2021/5/17

- Improve static request dispatch ([pull #54][pull_54]).

[pull_54]: https://github.com/apiflask/apiflask/pull/54


## Version 0.6.2

Released: 2021/5/16

- Fix static request dispatch for Flask 2.0 ([issue #52][issue_52]).

[issue_52]: https://github.com/apiflask/apiflask/issues/52


## Version 0.6.1

Released: 2021/5/15

- Fix type annotaion for Flask 2.0 ([pull #48][pull_48]).
- Fix type annotaion for `schema` parameter of `input` and `output`
([pull #49][pull_49]).
- Fix type annotaion for imports by exporting top-level name explicitly
([pull #49][pull_49]).
- Fix async for `dispatch_request` for Flask 2.0 ([pull #50][pull_50]).

[pull_48]: https://github.com/apiflask/apiflask/pull/48
[pull_49]: https://github.com/apiflask/apiflask/pull/49
[pull_50]: https://github.com/apiflask/apiflask/pull/50


## Version 0.6.0

Released: 2021/5/11

- Support using the `output` decorator on async views ([pull #41][pull_41]).
- Add `PaginationSchema` and `pagination_builder` as basic pagination support
  ([pull #42][pull_42]).
- Import and rename the decorators from marshmallow ([pull #43][pull_43]).
- Rename `utils` module to `helpers` ([pull #44][pull_44]).
- Add `default` parameter for `get_reason_phrase` ([pull #45][pull_45]).

[pull_41]: https://github.com/apiflask/apiflask/pull/41
[pull_42]: https://github.com/apiflask/apiflask/pull/42
[pull_43]: https://github.com/apiflask/apiflask/pull/43
[pull_44]: https://github.com/apiflask/apiflask/pull/44
[pull_45]: https://github.com/apiflask/apiflask/pull/45


## Version 0.5.2

Released: 2021/4/29

- Allow returning a `Response` object in a view function decorated with the `output`
  decorator. In this case, APIFlask will do nothing but return it directly
  ([pull #38][pull_38]).
- Skip Flask's `Blueprint` object when generating the OpenAPI spec ([pull #37][pull_37]).

[pull_38]: https://github.com/apiflask/apiflask/pull/38
[pull_37]: https://github.com/apiflask/apiflask/pull/37


## Version 0.5.1

Released: 2021/4/28

- Change the default endpoint of the view class to the original class name
  ([pull #36][pull_36]).
- Allow passing the `methods` argument for the `route` decorator on view classes.

[pull_36]: https://github.com/apiflask/apiflask/pull/36


## Version 0.5.0

Released: 2021/4/27

- Remove the support to generate `info.description` and tag description from module
  docstring, and also remove the `AUTO_DESCRIPTION` config ([pull #30][pull_30]).
- Remove the configuration variable `DOCS_HIDE_BLUEPRINTS`, add `APIBlueprint.enable_openapi`
  as a replacement.
- Support class-based views, now the `route` decorator can be used on `MethodView` class.
  Other decorators (i.e., `@input`, `@output`, etc.) can be used on view methods
  (i.e., `get()`, `post()`, etc.) ([pull #32][pull_32]).
- No longer support to mix the use of `flask.Bluerpint` and `apiflask.APIBluerpint`.
- Support to use the `auth_required` decorator on app-wide `before_request` functions
([pull #34][pull_34]).

[pull_30]: https://github.com/apiflask/apiflask/pull/30
[pull_32]: https://github.com/apiflask/apiflask/pull/32
[pull_34]: https://github.com/apiflask/apiflask/pull/34


## Version 0.4.0

Released: 2021/4/20

- Merge the following configuration variables to `SUCCESS_DESCRIPTION` ([pull #7][pull_7]):
    - `DEFAULT_2XX_DESCRIPTION`
    - `DEFAULT_200_DESCRIPTION`
    - `DEFAULT_201_DESCRIPTION`
    - `DEFAULT_204_DESCRIPTION`
- Remove the following configuration variables ([pull #7][pull_7]):
    - `AUTO_HTTP_ERROR_RESPONSE`
    - `AUTH_ERROR_SCHEMA`
- Add new configuration variables `YAML_SPEC_MIMETYPE` and `JSON_SPEC_MIMETYPE` to support
  to customize the MIME type of spec response ([pull #3][pull_3]).
- Remove configuration variable `SPEC_TYPE`.
- Fix the support to pass an empty dict as schema for 204 response ([pull #12][pull_12]).
- Support set multiple examples for request/response body with `@output(examples=...)`
  and `@iniput(examples=...)` ([pull #23][pull_23]).
- Add `auth_required(roles=...)` and `doc(tags=...)` parameters for list value, `role` and
  `tag` parameter now only accept string value ([pull #26][pull_26]).
- Add new configuration variable `OPENAPI_VERSION` to set the version of OAS
  ([pull #27][pull_27]).
- Rename `abort_json()` to `abort()` ([pull #29][pull_29]).

[pull_3]: https://github.com/apiflask/apiflask/pull/3
[pull_12]: https://github.com/apiflask/apiflask/pull/12
[pull_7]: https://github.com/apiflask/apiflask/pull/7
[pull_23]: https://github.com/apiflask/apiflask/pull/23
[pull_26]: https://github.com/apiflask/apiflask/pull/26
[pull_27]: https://github.com/apiflask/apiflask/pull/27
[pull_29]: https://github.com/apiflask/apiflask/pull/29


## Version 0.3.0

Released: 2021/3/31

- First public version.
- Add type annotations and enable type check in tox ([commit](https://github.com/apiflask/apiflask/commit/5cbf27ecbb4318a9fd177307a52146aa993f86c8)).
- Refactor the APIs ([commit](https://github.com/apiflask/apiflask/commit/d149c0c0ee90a7120e6ede1c3e09715c944bb704)):
    - Change base class `scaffold.Scaffold` to class decorator `utils.route_shortcuts`.
    - Merge the `_OpenAPIMixin` class into `APIFlask` class.
    - Turn `security._AuthErrorMixin` into `handle_auth_error` function.
    - Add explicit parameter `role` and `optional` for `@auth_required` decorator.
    - Rename module `errors` to `exceptions`.
    - Rename `api_abort()` to `abort_json()`.
    - Rename `get_error_message()` to `get_reason_phrase()` and move it to `utils` module.
    - Update the default value of config `AUTH_ERROR_DESCRIPTION`.
    - Add `validators` module.
    - Change `@doc(tags)` to `@doc(tag)`.
- Support to pass a dict schema in `@output` decorator ([commit](https://github.com/apiflask/apiflask/commit/e82fd168faf5f04871e549ebe22c63e66270bd1b)).
- Support to pass a dict schema in `@input` decorator ([commit](https://github.com/apiflask/apiflask/commit/f9c2c441363ddf4720800e0d3fc3d0e9cc28fe81)).
- Check if the status code is valid for `abort_json` and `HTTPError` ([commit](https://github.com/apiflask/apiflask/commit/20077dea0e82f123a3d2fc50c2ec529346215789)).
- Add basic docstrings to generate the API reference documentation ([commit](https://github.com/apiflask/apiflask/commit/6d65a25ab4de9d623e22575d4d5476abdc50cbc0)).
- Support to set custom example for request/response body ([commit](https://github.com/apiflask/apiflask/commit/638fa9c5680944d6454a4dbafe8abb152525d91c)).


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
    - `AUTO_OPERATION_SUMMARY`
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
- Support to hide blueprint from API docs with config `DOCS_HIDE_BLUEPRINTS` ([commit](https://github.com/apiflask/apiflask/commit/3b2cc0097defaabf0b916e00930dda1da8226430))
- Support to deprecate and hide an endpoint with `doc(hide=True, deprecated=True)`([commit](https://github.com/apiflask/apiflask/commit/82d181a7080bd4088ee8db929e81431a723cda93))
- Support to customize the API docs with various configuration variables. ([commit](https://github.com/apiflask/apiflask/commit/294379428f5032c6c8228841a836a37860012c0f))
- Support to set all fields of OpenAPI object and Info object ([commit](https://github.com/apiflask/apiflask/commit/a7990e28e73bdd5b86c1471aa97861025e14295f))
- Support YAML format spec ([commit](https://github.com/apiflask/apiflask/commit/ce6975bb465e01b0e48b2b8adce0f99a8db56e01))
- Automatically register a validation error response for endpoints which use `@input`. ([commit](https://github.com/apiflask/apiflask/commit/c3d7c3b585ca5d7f9f6d84f16137dd257bfe0518))
- Automatically register a authorization error response for endpoints which use `@auth_required`. ([commit](https://github.com/apiflask/apiflask/commit/c8992a8e420522a3e66563e455aa628f0f20a09c))
- Automatically add response schema for responses added with `@doc(responses=...)`. ([commit](https://github.com/apiflask/apiflask/commit/1b7dce5f722d038be5dc726d52a0eefd0365eeeb))
- Pass view arguments to view function as positional arguments ([commit](https://github.com/apiflask/apiflask/commit/15c66f3ba97310ed10c851721177e6c504a87317))
- Require Python 3.7 to use ordered dict ([commit](https://github.com/apiflask/apiflask/commit/557a7e649b64aef8f4b8596a4af175524d108ff4))
- Add shortcuts for `app.route`: `app.get()`, `app.post()`, etc. ([commit](https://github.com/apiflask/apiflask/commit/48bc1246628e53573c811def4a909be0faa9dcfb))
- Not an extension any more ([commit](https://github.com/apiflask/apiflask/commit/ecaec37544524deb8b2ce445d4a3cbf990ff95cb))


## Version 0.1.0

Released: 2021-1-27

- Add view functions without response schema into spec ([commit](https://github.com/apiflask/apiflask/commit/aabf427590227001e0e443d8d6a3bf5f56dc5964))
- Set default response descriptions ([commit](https://github.com/apiflask/apiflask/commit/b9edf9e8f5731a8f45b359f6a101b4d39ba3f2f5))
- Stop relying on Flask-Marshmallow ([commit](https://github.com/apiflask/apiflask/commit/cce7a0b8b97f345e087973b127c6d25c884dbc8f))
- Change default spec path to `openapi.json` ([commit](https://github.com/apiflask/apiflask/commit/09d0d278a1fc27fa5868ef5848f3931bd8f76ef4))
- Add support for enabling Swagger UI and Redoc at the same time ([commit](https://github.com/apiflask/apiflask/commit/d5176418b8c22e523d8b82e1f9af8f2403fa70bb))
- Change default spec title and version ([commit](https://github.com/apiflask/apiflask/commit/0953c310327539f96bcdfad142772c7800285d56))
- Support auto generating summary from function name ([commit](https://github.com/apiflask/apiflask/commit/d3d7cc2f63f3cf26466e42d68a03b4d96bf2fd97))
- Start as a fork of [APIFairy 0.6.2](https://github.com/miguelgrinberg/APIFairy/releases/tag/v0.6.2) at 2021-01-13.
