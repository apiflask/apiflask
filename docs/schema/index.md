# Data Schema

Read [this section](/usage/#use-appinput-to-validate-and-deserialize-request-data) and following
section first in the Basic Usage chapter for the basics of writing input and output schema.

## Schema Types Support

APIFlask supports multiple schema types through a adapter system:

- **marshmallow schemas**: Full backward compatibility with existing APIFlask applications
- **Pydantic models**: Modern type-hint based validation and serialization

The schema adapter system automatically detects the schema type and handles validation, serialization, and OpenAPI spec generation accordingly.

## Basic concepts on data schema:

### marshmallow

- APIFlask's `apiflask.Schema` base class is directly imported from marshmallow with some minor changes,
  see the [API documentation](https://marshmallow.readthedocs.io/en/stable/marshmallow.schema.html)
  for the details.
- We recommend separating input and output schema. Since the output data is not
  validated, you don't need to define validators on output fields.
- `apiflask.fields` includes all the fields provided by marshmallow, webargs, and
  flask-marshmallow (while some aliases were removed).
- `apiflask.validators` includes all the validators in `marshmallow.validate`.
- For other functions/classes, just import them from marshmallow.
- Read [marshmallow's documentation](https://marshmallow.readthedocs.io/) for details.

### Pydantic

- Define data models using Python type hints and Pydantic's `BaseModel`.
- We recommend separating input and output schema. Since the output data is not
  validated, you don't need to define validators on output fields.
- Built-in validation based on Python types with optional custom validators.
- Read [Pydantic's documentation](https://docs.pydantic.dev/) for comprehensive information.
