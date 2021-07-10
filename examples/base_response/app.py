from apiflask import APIFlask, Schema, input, output, abort
from apiflask.fields import Integer, String, Field
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)


class BaseResponseSchema(Schema):
    message = String()
    status_code = Integer()
    data = Field()  # the data key


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


def make_resp(message, status_code, data):
    # the return value should match the base response schema
    # and the data key should match
    return {'message': message, 'status_code': status_code, 'data': data}


@app.get('/')
def say_hello():
    data = {'message': 'Hello!'}
    return make_resp('Success!', 200, data)


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return make_resp('Success!', 200, pets[pet_id])


@app.get('/pets')
@output(PetOutSchema(many=True))
def get_pets():
    return make_resp('Success!', 200, pets)


@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data):
    pet_id = len(pets)
    data['id'] = pet_id
    pets.append(data)
    return make_resp('Pet created.', 201, pets[pet_id])


@app.patch('/pets/<int:pet_id>')
@input(PetInSchema(partial=True))
@output(PetOutSchema)
def update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return make_resp('Pet updated.', 200, pets[pet_id])


@app.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['deleted'] = True
    pets[pet_id]['name'] = 'Ghost'
    return ''
