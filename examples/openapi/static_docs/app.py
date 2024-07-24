from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
app.config['LOCAL_SPEC_JSON_INDENT'] = 0

pets = [{'id': 0, 'name': 'Kitty', 'category': 'cat'}, {'id': 1, 'name': 'Coco', 'category': 'dog'}]


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/')
def say_hello():
    # returning a dict or list equals to use jsonify()
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    if pet_id > len(pets) - 1:
        abort(404)
    # you can also return an ORM/ODM model class instance directly
    # APIFlask will serialize the object into JSON format
    return pets[pet_id]


@app.patch('/pets/<int:pet_id>')
@app.input(PetIn(partial=True))  # -> json_data
@app.output(PetOut)
def update_pet(pet_id, json_data):
    # the validated and parsed input data will
    # be injected into the view function as a dict
    if pet_id > len(pets) - 1:
        abort(404)
    for attr, value in json_data.items():
        pets[pet_id][attr] = value
    return pets[pet_id]


if __name__ == '__main__':
    app.run()
