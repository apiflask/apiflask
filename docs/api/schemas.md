# Schemas

This module contains the built-in marshmallow Schema class and related helpers. APIFlask also supports Pydantic models through the [schema adapter system](/api/schema_adapters).

::: apiflask.schemas

## Schema Types Support

APIFlask supports multiple schema types:

- **Marshmallow schemas**: Traditional field-based schemas using the `apiflask.Schema` class
- **Pydantic models**: Modern type-hint based models using `pydantic.BaseModel`
- **Mixed usage**: You can use both types in the same application

The choice of schema type is automatically detected by the schema adapter system.

## External documentation

### Marshmallow Documentation

Check out the API docs for `Schema` class in the marshmallow docs:

- Schema: <https://marshmallow.readthedocs.io/en/stable/marshmallow.schema.html>
- Decorators: <https://marshmallow.readthedocs.io/marshmallow.decorators.html>

### Pydantic Documentation

For Pydantic models, see:

- Models: <https://docs.pydantic.dev/usage/models/>
- Field Types: <https://docs.pydantic.dev/usage/types/>
- Validators: <https://docs.pydantic.dev/usage/validators/>
