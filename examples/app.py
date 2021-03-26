from apiflask import APIFlask, input, output, Schema, api_abort
from apiflask.fields import Integer, String

app = APIFlask(__name__)

pets = [
    {
        'id': 0,
        'name': 'Kitty',
        'category': 'cat'
    },
    {
        'id': 1,
        'name': 'Coco',
        'category': 'dog'
    },
    {
        'id': 2,
        'name': 'Flash',
        'category': 'cat'
    }
]


class PetSchema(Schema):
    id = Integer(required=True, dump_only=True)
    name = String(required=True)
    category = String(required=True)


@app.get('/pets/<int:pet_id>')
@output(PetSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1:
        api_abort(404)
    return pets[pet_id]


@app.get('/pets')
@output(PetSchema(many=True))
def get_pets():
    return pets


@app.post('/pets')
@input(PetSchema)
@output(PetSchema, 201)
def create_pet(pet):
    pet['id'] = len(pets) + 1
    pets.append(pet)
    return pet


@app.put('/pets/<int:pet_id>')
@input(PetSchema)
@output(PetSchema)
def update_pet(pet_id, pet):
    if pet_id > len(pets):
        api_abort(404)
    pet['id'] = pet_id
    pets[pet_id] = pet
    return pet


@app.patch('/pets/<int:pet_id>')
@input(PetSchema(partial=True))
@output(PetSchema)
def partial_update_pet(pet_id, pet):
    if pet_id > len(pets):
        api_abort(404)
    for attr, value in pet:
        pets[pet_id][attr] = value
    return pets[pet_id]


@app.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets):
        api_abort(404)
    pets.pop(pet_id)
    return ''
