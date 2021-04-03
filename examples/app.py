from apiflask import APIFlask, Schema, input, output, abort_json
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

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


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort_json(404)
    return pets[pet_id]


@app.get('/pets')
@output(PetOutSchema(many=True))
def get_pets():
    return pets


@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data):
    data['id'] = len(pets)
    pets.append(data)
    return data


@app.put('/pets/<int:pet_id>')
@input(PetInSchema)
@output(PetOutSchema)
def update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort_json(404)
    data['id'] = pet_id
    pets[pet_id] = data
    return data


@app.patch('/pets/<int:pet_id>')
@input(PetInSchema(partial=True))
@output(PetOutSchema)
def partial_update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort_json(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]


@app.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort_json(404)
    pets.pop(pet_id)
    return ''
