from .schemas import http_error_schema


# OpenAPI fields
DESCRIPTION = None
TAGS = None
CONTACT = None
LICENSE = None
SERVERS = None
EXTERNAL_DOCS = None
TERMS_OF_SERVICE = None
SPEC_FORMAT = 'json'
# Automation behaviour control
AUTO_TAGS = True
AUTO_DESCRIPTION = True
AUTO_PATH_SUMMARY = True
AUTO_PATH_DESCRIPTION = True
AUTO_200_RESPONSE = True
# Response customization
DEFAULT_200_DESCRIPTION = 'Successful response'
DEFAULT_204_DESCRIPTION = 'Empty response'
AUTO_VALIDATION_ERROR_RESPONSE = True
VALIDATION_ERROR_STATUS_CODE = 400
VALIDATION_ERROR_DESCRIPTION = 'Validation error'
VALIDATION_ERROR_SCHEMA = http_error_schema
AUTO_AUTH_ERROR_RESPONSE = True
AUTH_ERROR_STATUS_CODE = 401
AUTH_ERROR_DESCRIPTION = 'Authorization error'
AUTH_ERROR_SCHEMA = http_error_schema
# Swagger UI and Redoc
DOCS_HIDE_BLUEPRINTS = []
DOCS_FAVICON = None
REDOC_USE_GOOGLE_FONT = True
REDOC_STANDALONE_JS = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/\
redoc.standalone.js'
SWAGGER_UI_CSS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
SWAGGER_UI_BUNDLE_JS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-bundle.js'
SWAGGER_UI_STANDALONE_PRESET_JS = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/\
swagger-ui-standalone-preset.js'
SWAGGER_UI_LAYOUT = 'BaseLayout'
SWAGGER_UI_CONFIG = None
SWAGGER_UI_OAUTH_CONFIG = None
