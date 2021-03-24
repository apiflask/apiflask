from flask_marshmallow import Schema


validation_error_detail_schema = {
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


validation_error_schema = {
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


http_error_schema = {
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
