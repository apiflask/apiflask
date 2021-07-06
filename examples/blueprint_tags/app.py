from apiflask import APIFlask, APIBlueprint, Schema, input, output, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)
hello_bp = APIBlueprint('hello', __name__)  # tag name will be "Hello"
pet_bp = APIBlueprint('pet', __name__)  # tag name will be "Pet"

# The default tag is the blueprint name in title form. If you need to set a custom tag name:
# hello_bp = APIBlueprint('hello', __name__, tag='NoHello')

# If you need to set the tag "description" or "externalDocs", just pass a dict:
# hello_bp = APIBlueprint('hello', __name__, tag={'name': 'Hello', 'description': '...'})
# pet_bp = APIBlueprint('pet', __name__, tag={'name': 'Pet', 'description': '...'})

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


@hello_bp.get('/')
def say_hello():
    return {'message': 'Hello!'}


@pet_bp.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
        abort(404)
    return pets[pet_id]


@pet_bp.get('/pets')
@output(PetOutSchema(many=True))
def get_pets():
    return pets


@pet_bp.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data):
    pet_id = len(pets)
    data['id'] = pet_id
    pets.append(data)
    return pets[pet_id]


@pet_bp.patch('/pets/<int:pet_id>')
@input(PetInSchema(partial=True))
@output(PetOutSchema)
def update_pet(pet_id, data):
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]


@pet_bp.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    pets[pet_id]['deleted'] = True
    pets[pet_id]['name'] = 'Ghost'
    return ''


app.register_blueprint(hello_bp)
app.register_blueprint(pet_bp)
