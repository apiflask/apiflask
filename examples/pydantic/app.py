from enum import Enum

from apiflask import APIFlask, abort
from pydantic import BaseModel, Field

app = APIFlask(__name__)


class PetCategory(str, Enum):
    DOG = 'dog'
    CAT = 'cat'


class PetOut(BaseModel):
    id: int
    name: str
    category: PetCategory


class PetIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    category: PetCategory


pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Buddy', 'category': 'dog'},
]


@app.get('/')
def say_hello():
    return {'message': 'Hello, Pydantic!'}


@app.get('/pets')
@app.output(list[PetOut])
def get_pets():
    return pets


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id: int):
    if pet_id > len(pets) or pet_id < 1:
        abort(404)
    return pets[pet_id - 1]


@app.post('/pets')
@app.input(PetIn, location='json')
@app.output(PetOut, status_code=201)
def create_pet(json_data: PetIn):
    print(type(json_data))
    new_id = len(pets) + 1
    new_pet = PetOut(id=new_id, name=json_data.name, category=json_data.category)
    pets.append(new_pet)
    return new_pet


@app.patch('/pets/<int:pet_id>')
@app.input(PetIn, location='json')
@app.output(PetOut)
def update_pet(pet_id: int, json_data: PetIn):
    if pet_id > len(pets) or pet_id < 1:
        abort(404)

    pet = pets[pet_id - 1]
    pet.name = json_data.name
    pet.category = json_data.category
    return pet


@app.delete('/pets/<int:pet_id>')
@app.output({}, status_code=204)
def delete_pet(pet_id: int):
    if pet_id > len(pets) or pet_id < 1:
        abort(404)

    pets.pop(pet_id - 1)
    return ''
