from typing import List
from enum import Enum

from apiflask import APIFlask, abort
from pydantic import BaseModel, Field

app = APIFlask(__name__)


class BaseResponse(BaseModel):
    data: object  # the data key
    message: str
    code: int


app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse
# the data key should match the data field name in the base response schema
# defaults to "data"
app.config['BASE_RESPONSE_DATA_KEY'] = 'data'

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'},
    {'id': 2, 'name': 'Flash', 'category': 'cat'},
]


class PetCategory(str, Enum):
    cat = 'cat'
    dog = 'dog'


class PetIn(BaseModel):
    name: str = Field(min_length=1, max_length=10)
    category: PetCategory


class PetOut(BaseModel):
    id: int
    name: str
    category: PetCategory


@app.get('/')
def say_hello():
    data = {'message': 'Hello!'}
    return {'data': data, 'message': 'Success!', 'code': 200}


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return {
        'data': pets[pet_id],
        'message': 'Success!',
        'code': 200,
    }


@app.get('/pets')
@app.output(List[PetOut])
def get_pets():
    return {
        'data': pets,
        'message': 'Success!',
        'code': 200,
    }


@app.post('/pets')
@app.input(PetIn, location='json')
@app.output(PetOut, status_code=201)
def create_pet(json_data):
    new_id = len(pets) + 1
    new_pet = PetOut(id=new_id, name=json_data.name, category=json_data.category)
    pets.append(new_pet)
    return {'data': new_pet, 'message': 'Pet created.', 'code': 201}


@app.patch('/pets/<int:pet_id>')
@app.input(PetIn, location='json')
@app.output(PetOut)
def update_pet(pet_id, json_data):
    if pet_id > len(pets) - 1:
        abort(404)

    pet = pets[pet_id]
    pet['name'] = json_data.name
    pet['category'] = json_data.category
    return {'data': pet, 'message': 'Pet updated.', 'code': 200}


@app.delete('/pets/<int:pet_id>')
@app.output({}, status_code=204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['deleted'] = True
    pets[pet_id]['name'] = 'Ghost'
    return ''
