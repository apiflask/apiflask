from typing import Dict, Any

from marshmallow import Schema


validation_error_detail_schema: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "<location>": {
            "type": "object",
            "properties": {
                "<field_name>": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    }
}


validation_error_schema: Dict[str, Any] = {
    "properties": {
        "detail": validation_error_detail_schema,
        "message": {
            "type": "string"
        },
        "status_code": {
            "type": "integer"
        }
    },
    "type": "object"
}


http_error_schema: Dict[str, Any] = {
    "properties": {
        "detail": {
            "type": "object"
        },
        "message": {
            "type": "string"
        },
        "status_code": {
            "type": "integer"
        }
    },
    "type": "object"
}


class EmptySchema(Schema):
    pass
