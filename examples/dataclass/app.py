from dataclasses import field

from marshmallow_dataclass import dataclass

from apiflask import APIFlask, abort
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


@dataclass
class PetInDataclass:
    name: str = field(metadata={'required': True, 'validate': Length(min=1, max=10)})
    category: str = field(
        metadata={'required': True, 'validate': OneOf(['cat', 'dog'])}
    )


@dataclass
class PetOutDataclass:
    id: int
    name: str
    category: str


pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'},
    {'id': 2, 'name': 'Flash', 'category': 'cat'}
]


@app.get('/')
def say_hello():
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@app.output(PetOutDataclass.Schema())
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or hasattr(pets[pet_id], 'deleted'):
        abort(404)
    return pets[pet_id]


@app.get('/pets')
@app.output(PetOutDataclass.Schema(many=True))
def get_pets():
    return pets


@app.post('/pets')
@app.input(PetInDataclass.Schema())
@app.output(PetOutDataclass.Schema(), 201)
def create_pet(data):
    pet_id = len(pets)
    pets[pet_id].name = data.name
    pets[pet_id].category = data.category

    return pets[pet_id]


@app.patch('/pets/<int:pet_id>')
@app.input(PetInDataclass.Schema(partial=True))
@app.output(PetOutDataclass.Schema())
def update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort(404)
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]


@app.delete('/pets/<int:pet_id>')
@app.output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id].name = 'ghost'
    pets[pet_id].deleted = True
    return ''
