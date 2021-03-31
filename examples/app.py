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
    }
]


class PetInSchema(Schema):
    name = String(required=True, validators=Length(0, 10))
    category = String(required=True, validators=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    if pet_id > len(pets):
        abort_json(404)
    return pets[pet_id]


@app.post('/pets/<int:pet_id>')
@input(PetInSchema)
@output(PetOutSchema)
def update_pet(pet_id, pet):
    if pet_id > len(pets):
        abort_json(404)
    pet['id'] = pet_id
    pets[pet_id] = pet
    return pet





# from apiflask import APIFlask, input, output, Schema, abort_json
# from apiflask.fields import Integer, String
# from apiflask.validators import Length, OneOf

# app = APIFlask(__name__)

# pets = [
#     {
#         'id': 0,
#         'name': 'Kitty',
#         'category': 'cat'
#     },
#     {
#         'id': 1,
#         'name': 'Coco',
#         'category': 'dog'
#     },
#     {
#         'id': 2,
#         'name': 'Flash',
#         'category': 'cat'
#     }
# ]


# class PetInSchema(Schema):
#     name = String(required=True, validate=Length(0, 10))
#     category = String(required=True, validate=OneOf(['dog', 'cat']))


# class PetOutSchema(Schema):
#     id = Integer()
#     name = String()
#     category = String()


# @app.get('/pets/<int:pet_id>')
# @output(PetOutSchema)
# def get_pet(pet_id):
#     if pet_id > len(pets) - 1:
#         abort_json(404)
#     return pets[pet_id]


# @app.get('/pets')
# @output(PetOutSchema(many=True))
# def get_pets():
#     return pets


# @app.post('/pets')
# @input(PetInSchema)
# @output(PetOutSchema, 201)
# def create_pet(pet):
#     pet['id'] = len(pets) + 1
#     pets.append(pet)
#     return pet


# @app.put('/pets/<int:pet_id>')
# @input(PetInSchema)
# @output(PetOutSchema)
# def update_pet(pet_id, pet):
#     if pet_id > len(pets):
#         abort_json(404)
#     pet['id'] = pet_id
#     pets[pet_id] = pet
#     return pet


# @app.patch('/pets/<int:pet_id>')
# @input(PetInSchema(partial=True))
# @output(PetOutSchema)
# def partial_update_pet(pet_id, pet):
#     if pet_id > len(pets):
#         abort_json(404)
#     for attr, value in pet:
#         pets[pet_id][attr] = value
#     return pets[pet_id]


# @app.delete('/pets/<int:pet_id>')
# # @output({}, 204)
# @output({'id': String(default=3), 'name': String(required=True)})
# def delete_pet(pet_id):
#     if pet_id > len(pets):
#         abort_json(404)
#     pets.pop(pet_id)
#     return ''
