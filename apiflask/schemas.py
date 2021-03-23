from flask_marshmallow import Schema


validation_error_schema = {
    "type": "object",
    "properties": {
        "detail": {
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
    }
}


http_error_schema = {
    "properties": {
        "detail": validation_error_schema["properties"]["detail"],
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
