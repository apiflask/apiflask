from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String, Field
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


class BaseResponseSchema(Schema):
    data = Field()  # the data key
    message = String()
    code = Integer()


app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
# the data key should match the data field name in the base response schema
# defaults to "data"
app.config['BASE_RESPONSE_DATA_KEY '] = 'data'

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'},
    {'id': 2, 'name': 'Flash', 'category': 'cat'}
]


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/')
def say_hello():
    data = {'message': 'Hello!'}
    return {
        'data': data,
        'message': 'Success!',
        'code': 200
    }


@app.get('/pets/<int:pet_id>')
@app.output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return {
        'data': pets[pet_id],
        'message': 'Success!',
        'code': 200,
    }


@app.get('/pets')
@app.output(PetOutSchema(many=True))
def get_pets():
    return {
        'data': pets,
        'message': 'Success!',
        'code': 200,
    }


@app.post('/pets')
@app.input(PetInSchema)
@app.output(PetOutSchema, 201)
def create_pet(data):
    pet_id = len(pets)
    data['id'] = pet_id
    pets.append(data)
    return {
        'data': pets[pet_id],
        'message': 'Pet created.',
        'code': 201
    }


@app.patch('/pets/<int:pet_id>')
@app.input(PetInSchema(partial=True))
@app.output(PetOutSchema)
def update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return {
        'data': pets[pet_id],
        'message': 'Pet updated.',
        'code': 200
    }


@app.delete('/pets/<int:pet_id>')
@app.output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['deleted'] = True
    pets[pet_id]['name'] = 'Ghost'
    return ''
