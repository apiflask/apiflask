from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from apiflask import APIFlask, abort

app = APIFlask(__name__)


# Pydantic models
class Pet(BaseModel):
    id: int
    name: str
    category: str

    model_config = {'json_schema_extra': {'example': {'id': 1, 'name': 'Coco', 'category': 'dog'}}}


class PetIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description='Pet name')
    category: str = Field(..., description='Pet category')

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed = ['dog', 'cat', 'bird', 'fish']
        if v not in allowed:
            raise ValueError(f'Category must be one of {allowed}')
        return v

    model_config = {'json_schema_extra': {'example': {'name': 'Coco', 'category': 'dog'}}}


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserIn(BaseModel):
    name: str
    email: EmailStr


class QueryParams(BaseModel):
    category: Optional[str] = None
    limit: int = 10


# Sample data
pets = [Pet(id=1, name='Kitty', category='cat'), Pet(id=2, name='Coco', category='dog')]


@app.get('/')
def say_hello():
    """Say hello."""
    return {'message': 'Hello, Pydantic!'}


@app.get('/pets')
@app.input(QueryParams, location='query')
@app.output(Pet)
def get_pets(query_data):
    """Get all pets with optional filtering."""
    filtered_pets = pets

    if query_data.category:
        filtered_pets = [p for p in pets if p.category == query_data.category]

    return filtered_pets[: query_data.limit]


@app.get('/pets/<int:pet_id>')
@app.output(Pet)
def get_pet(pet_id):
    """Get a pet by ID."""
    if pet_id > len(pets) or pet_id < 1:
        abort(404)
    return pets[pet_id - 1]


@app.post('/pets')
@app.input(PetIn, location='json')
@app.output(Pet, status_code=201)
def create_pet(json_data):
    """Create a new pet."""
    new_id = len(pets) + 1
    new_pet = Pet(id=new_id, name=json_data.name, category=json_data.category)
    pets.append(new_pet)
    return new_pet


@app.patch('/pets/<int:pet_id>')
@app.input(PetIn, location='json')
@app.output(Pet)
def update_pet(pet_id, json_data):
    """Update a pet."""
    if pet_id > len(pets) or pet_id < 1:
        abort(404)

    pet = pets[pet_id - 1]
    pet.name = json_data.name
    pet.category = json_data.category
    return pet


@app.delete('/pets/<int:pet_id>')
def delete_pet(pet_id):
    """Delete a pet."""
    if pet_id > len(pets) or pet_id < 1:
        abort(404)

    pets.pop(pet_id - 1)
    return '', 204


# Example with form data
@app.post('/pets/form')
@app.input(PetIn, location='form')
@app.output(Pet, status_code=201)
def create_pet_form(form_data):
    """Create a pet from form data."""
    new_id = len(pets) + 1
    new_pet = Pet(id=new_id, name=form_data.name, category=form_data.category)
    pets.append(new_pet)
    return new_pet


if __name__ == '__main__':
    app.run(debug=True)
