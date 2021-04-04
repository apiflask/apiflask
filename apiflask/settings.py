from typing import List
from typing import Optional
from typing import Dict

from .schemas import http_error_schema
from .schemas import validation_error_schema
from .types import SchemaType
from .types import TagsType


# OpenAPI fields
DESCRIPTION: Optional[str] = None
TAGS: Optional[TagsType] = None
CONTACT: Optional[Dict[str, str]] = None
LICENSE: Optional[Dict[str, str]] = None
SERVERS: Optional[List[Dict[str, str]]] = None
EXTERNAL_DOCS: Optional[Dict[str, str]] = None
TERMS_OF_SERVICE: Optional[str] = None
YAML_SPEC_MIMETYPE: str = 'text/vnd.yaml'
JSON_SPEC_MIMETYPE: str = 'application/json'
# Automation behaviour control
AUTO_TAGS: bool = True
AUTO_DESCRIPTION: bool = True
AUTO_PATH_SUMMARY: bool = True
AUTO_PATH_DESCRIPTION: bool = True
AUTO_200_RESPONSE: bool = True
# Response customization
DEFAULT_2XX_DESCRIPTION: str = 'Successful response'
DEFAULT_200_DESCRIPTION: str = 'Successful response'
DEFAULT_201_DESCRIPTION: str = 'Resource created'
DEFAULT_204_DESCRIPTION: str = 'Empty response'
AUTO_VALIDATION_ERROR_RESPONSE: bool = True
VALIDATION_ERROR_STATUS_CODE: int = 400
VALIDATION_ERROR_DESCRIPTION: str = 'Validation error'
VALIDATION_ERROR_SCHEMA: SchemaType = validation_error_schema
AUTO_AUTH_ERROR_RESPONSE: bool = True
AUTH_ERROR_STATUS_CODE: int = 401
AUTH_ERROR_DESCRIPTION: str = 'Authentication error'
AUTH_ERROR_SCHEMA: SchemaType = http_error_schema
AUTO_HTTP_ERROR_RESPONSE: bool = True
HTTP_ERROR_SCHEMA: SchemaType = http_error_schema
# Swagger UI and Redoc
DOCS_HIDE_BLUEPRINTS: List[str] = []
DOCS_FAVICON: Optional[str] = None
REDOC_USE_GOOGLE_FONT: bool = True
REDOC_STANDALONE_JS: str = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/\
redoc.standalone.js'
SWAGGER_UI_CSS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
SWAGGER_UI_BUNDLE_JS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-bundle.js'
SWAGGER_UI_STANDALONE_PRESET_JS: str = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-standalone-preset.js'
SWAGGER_UI_LAYOUT: str = 'BaseLayout'
SWAGGER_UI_CONFIG: Optional[dict] = None
SWAGGER_UI_OAUTH_CONFIG: Optional[dict] = None
