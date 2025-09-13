# Design Proposal

### Pydantic support

Target version: 3.0.0

Currently, the library does not support Pydantic models. This proposal aims to introduce Pydantic support to enhance data validation and serialization capabilities.

#### Implementation Details

- **Decoupling from Marshmallow**: Remove the direct dependency on Marshmallow and related libraries (webargs, apispec) for request and response validation. Create a common interface for validation and serialization that can be implemented by different libraries, including Pydantic, attr, etc.
- **Pydantic Model Integration**: Allow users to define Pydantic models for request and response bodies. The model can be passed to the APIFlask `app.input` and `app.output` decorators to handle validation and serialization automatically.
- **Automatic Validation**: Leverage Pydantic's validation features to automatically validate incoming request data.
- **Serialization**: Use Pydantic's serialization capabilities to serialize response data.
- **Error Handling**: Provide clear error messages for validation errors using Pydantic's error reporting.
- **OpenAPI Integration**: Ensure that the Pydantic models are compatible with OpenAPI specifications for automatic API documentation generation.
- **Documentation**: Update the documentation to include examples of using Pydantic models with the library.
- **Testing**: Add unit tests to ensure that Pydantic integration works as expected, including validation, serialization, error handling, OpenAPI generation, etc.
- **Backward Compatibility**: Ensure that existing functionality using Marshmallow remains intact, allowing users to choose between Marshmallow and Pydantic for validation and serialization.

#### Example Usage

New Pydantic support:

```python
from pydantic import BaseModel
from apiflask import APIFlask

app = APIFlask(__name__)


class UserModel(BaseModel):
    id: int
    name: str
    email: str


@app.get("/users/<user_id>")
@app.input(UserModel)
def get_user(json_data: UserModel):
    return json_data
```

Existing Marshmallow usage remains unchanged:

```python
from apiflask import APIFlask, fields
from apiflask.schema import Schema

app = APIFlask(__name__)


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Email()


@app.get("/users/<user_id>")
@app.input(UserSchema)
def get_user(json_data):
    return json_data
```

#### Related Files

- `src/apiflask/scaffold.py`: contains the definition of the `app.input` and `app.output` decorators. They are responsible for handling input and output validation and serialization.
- `src/apiflask/app.py`: contains the main application logic, including the resembling of the OpenAPI specification. Some of the OpenAPI generation logic are defined in `src/apiflask/openapi.py`.
- `src/apiflask/schema.py`: currently contains Marshmallow schema definitions. We can create a new module called `models.py` or extend this module to support Pydantic models.
