import typing as t

from .schemas import http_error_schema
from .schemas import validation_error_schema
from .types import OpenAPISchemaType
from .types import TagsType


# OpenAPI fields
OPENAPI_VERSION: str = '3.0.3'
SERVERS: t.Optional[t.List[t.Dict[str, str]]] = None
TAGS: t.Optional[TagsType] = None
EXTERNAL_DOCS: t.Optional[t.Dict[str, str]] = None
INFO: t.Optional[t.Dict[str, t.Union[str, dict]]] = None
DESCRIPTION: t.Optional[str] = None
TERMS_OF_SERVICE: t.Optional[str] = None
CONTACT: t.Optional[t.Dict[str, str]] = None
LICENSE: t.Optional[t.Dict[str, str]] = None
# OpenAPI spec
SPEC_FORMAT: str = 'json'
YAML_SPEC_MIMETYPE: str = 'text/vnd.yaml'
JSON_SPEC_MIMETYPE: str = 'application/json'
LOCAL_SPEC_PATH: t.Optional[str] = None
LOCAL_SPEC_JSON_INDENT: int = 2
SYNC_LOCAL_SPEC: t.Optional[bool] = None
# Automation behavior control
AUTO_TAGS: bool = True
AUTO_OPERATION_SUMMARY: bool = True
AUTO_OPERATION_DESCRIPTION: bool = True
AUTO_200_RESPONSE: bool = True
AUTO_404_RESPONSE: bool = True
AUTO_VALIDATION_ERROR_RESPONSE: bool = True
AUTO_AUTH_ERROR_RESPONSE: bool = True
# Response customization
SUCCESS_DESCRIPTION: str = 'Successful response'
NOT_FOUND_DESCRIPTION: str = 'Not found'
VALIDATION_ERROR_DESCRIPTION: str = 'Validation error'
AUTH_ERROR_DESCRIPTION: str = 'Authentication error'
VALIDATION_ERROR_STATUS_CODE: int = 400
AUTH_ERROR_STATUS_CODE: int = 401
VALIDATION_ERROR_SCHEMA: OpenAPISchemaType = validation_error_schema
HTTP_ERROR_SCHEMA: OpenAPISchemaType = http_error_schema
BASE_RESPONSE_SCHEMA: t.Optional[OpenAPISchemaType] = None
BASE_RESPONSE_DATA_KEY: str = 'data'
# Swagger UI and Redoc
DOCS_FAVICON: str = 'https://apiflask.com/_assets/favicon.png'
REDOC_USE_GOOGLE_FONT: bool = True
REDOC_STANDALONE_JS: str = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/\
redoc.standalone.js'
REDOC_CONFIG: t.Optional[dict] = None
SWAGGER_UI_CSS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
SWAGGER_UI_BUNDLE_JS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-bundle.js'
SWAGGER_UI_STANDALONE_PRESET_JS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-standalone-preset.js'
SWAGGER_UI_LAYOUT: str = 'BaseLayout'
SWAGGER_UI_CONFIG: t.Optional[dict] = None
SWAGGER_UI_OAUTH_CONFIG: t.Optional[dict] = None
