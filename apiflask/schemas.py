from flask_marshmallow.schema import Schema    # noqa: F401


validation_error_response_schema = {
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


class PaginationSchema(Schema):
    pass
