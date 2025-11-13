# Data Schema with Pydantic

## Using Pydantic Models

!!! warning "Version >= 3.0.0"

    Pydantic support was added in version 3.0.0 through the new schema adapter system.

!!! note "Pydantic 2.x"

    This documentation uses Pydantic 2.x (2.0+). If you're using Pydantic 1.x, please refer to the [Pydantic V2 migration guide](https://docs.pydantic.dev/latest/migration/).

APIFlask supports Pydantic models alongside marshmallow schemas. You can use Pydantic's type-hint based approach for defining data models and validation.

### Basic Pydantic Usage

Here's how to define and use Pydantic models with APIFlask:

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from apiflask import APIFlask

app = APIFlask(__name__)


class PetCategory(str, Enum):
    dog = 'dog'
    cat = 'cat'
    bird = 'bird'
    fish = 'fish'


class PetIn(BaseModel):
    name: str = Field(min_length=1, max_length=50, description='Pet name')
    category: PetCategory = Field(description='Pet category')
    age: Optional[int] = Field(default=None, ge=0, le=30, description='Pet age')


class PetOut(BaseModel):
    id: int = Field(description='Pet ID')
    name: str = Field(description='Pet name')
    category: PetCategory = Field(description='Pet category')
    age: Optional[int] = Field(default=None, description='Pet age')


@app.post('/pets')
@app.input(PetIn)
@app.output(PetOut, status_code=201)
def create_pet(json_data: PetIn):
    # json_data is automatically validated and deserialized into a PetIn instance
    new_pet = PetOut(
        id=1,
        name=json_data.name,
        category=json_data.category,
        age=json_data.age
    )
    return new_pet
```

### Pydantic Model Features

#### Type Hints and Validation

Pydantic uses Python type hints for automatic validation:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr  # Requires: pip install pydantic[email]
    age: int = Field(ge=18, le=120)
    website: Optional[HttpUrl] = None  # Requires: pip install pydantic[email]
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
```

#### Custom Validators

Pydantic 2.x provides `@field_validator` for field-level validation:

```python
from pydantic import BaseModel, field_validator, Field, ValidationError

class ProductIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    category: str

    @field_validator('name')
    @classmethod
    def name_must_be_alphanumeric(cls, v: str) -> str:
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric')
        return v.title()

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        categories = ['electronics', 'clothing', 'books', 'home']
        if v.lower() not in categories:
            raise ValueError(f'Category must be one of {categories}')
        return v.lower()
```

For more complex validation across multiple fields, use `@model_validator`:

```python
from datetime import datetime
from pydantic import BaseModel, model_validator, Field

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime
    min_duration_days: int = Field(default=1, ge=1)

    @model_validator(mode='after')
    def check_dates(self) -> 'DateRange':
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        duration = (self.end_date - self.start_date).days
        if duration < self.min_duration_days:
            raise ValueError(f'Duration must be at least {self.min_duration_days} days')
        return self
```

#### Nested Models

Pydantic supports nested models:

```python
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    category: str


class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class User(BaseModel):
    name: str
    email: str
    address: Address
    pets: list[Pet]
```

### Pydantic with Query Parameters

You can use Pydantic models for query parameters:

```python
from typing import Optional
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    q: str = Field(description='Search query')
    page: int = Field(default=1, ge=1, description='Page number')
    per_page: int = Field(default=10, ge=1, le=100, description='Items per page')
    sort_by: Optional[str] = Field(default=None, description='Sort field')

@app.get('/search')
@app.input(SearchQuery, location='query')
@app.output(SearchResultsOut)
def search(query_data):
    # query_data contains validated query parameters
    return perform_search(query_data)
```

### OpenAPI Schema Generation

Pydantic models automatically generate comprehensive OpenAPI schemas:

```python
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class Priority(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'

class Task(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'title': 'Complete project',
                    'description': 'Finish the API documentation',
                    'priority': 'high',
                    'completed': False,
                    'tags': ['work', 'urgent']
                }
            ]
        }
    )

    title: str = Field(description='Task title', examples=['Complete project'])
    description: Optional[str] = Field(default=None, description='Task description')
    priority: Priority = Field(default=Priority.medium, description='Task priority')
    completed: bool = Field(default=False, description='Task completion status')
    tags: list[str] = Field(default_factory=list, description='Task tags')
```

The above model will generate detailed OpenAPI schema with proper types, descriptions, examples, and enum values.

### Error Handling

Pydantic validation errors are automatically converted to APIFlask's standard error format:

```python
# When validation fails, you'll get structured error responses like:
{
    'message': 'Validation error',
    'detail': {
        'json': {
            'age': ['ensure this value is greater than or equal to 0'],
            'category': ['Category must be one of [\'dog\', \'cat\', \'bird\', \'fish\']']
        }
    }
}
```

### Complete Example

Check out [the complete Pydantic example application](https://github.com/apiflask/apiflask/tree/main/examples/pydantic/app.py)
for more details, see [the examples page](/examples) for running the example application.

### Documentation References

- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic Fields](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Field Types](https://docs.pydantic.dev/latest/concepts/types/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic Configuration](https://docs.pydantic.dev/latest/concepts/config/)
