from dataclasses import field

from marshmallow_dataclass import dataclass
from apiflask import APIFlask, abort
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


@dataclass
class PetIn:
    name: str = field(
        metadata={
            'required': True,
            'validate': Length(min=1, max=10),
            'example': 'Medor',
            'description': 'This will be printed in the generated doc. '
                           'The "example" value "Medor" will be fed '
                           'into the "try it"/"Send API request".',
        }
    )
    category: str = field(
        default='dog',
        metadata={
            'required': True,
            'validate': OneOf(['cat', 'dog'])
        }
    )


@dataclass
class PetOut:
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
@app.output(PetOut.Schema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return pets[pet_id]


@app.get('/pets')
@app.output(PetOut.Schema(many=True))
def get_pets():
    return pets


@app.post('/pets')
@app.input(PetIn.Schema, location='json', arg_name='pet')
@app.output(PetOut.Schema, status_code=201)
def create_pet(pet: PetIn):
    pet_id = len(pets)
    pets.append({
        'id': pet_id,
        'name': pet.name,
        'category': pet.category
    })
    return pets[pet_id]


# partial=True is not supported in marshmallow-dataclass currently
# https://github.com/lovasoa/marshmallow_dataclass/issues/169
@app.patch('/pets/<int:pet_id>')
@app.input(PetIn.Schema, location='json', arg_name='pet')
@app.output(PetOut.Schema)
def update_pet(pet_id, pet: PetIn):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['name'] = pet.name
    pets[pet_id]['category'] = pet.category
    return pets[pet_id]


@app.delete('/pets/<int:pet_id>')
@app.output({}, status_code=204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['deleted'] = True
    pets[pet_id]['name'] = 'Ghost'
    return ''
