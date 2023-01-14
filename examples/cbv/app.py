from apiflask import APIFlask, Schema, abort
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from apiflask.views import MethodView

app = APIFlask(__name__)

pets = [
    {'id': 0, 'name': 'Kitty', 'category': 'cat'},
    {'id': 1, 'name': 'Coco', 'category': 'dog'},
    {'id': 2, 'name': 'Flash', 'category': 'cat'}
]


class PetIn(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOut(Schema):
    id = Integer()
    name = String()
    category = String()


class Hello(MethodView):

    def get(self):
        return {'message': 'Hello!'}


class Pet(MethodView):

    @app.output(PetOut)
    def get(self, pet_id):
        """Get a pet"""
        if pet_id > len(pets) - 1 or pets[pet_id].get('deleted'):
            abort(404)
        return pets[pet_id]

    @app.input(PetIn(partial=True))
    @app.output(PetOut)
    def patch(self, pet_id, data):
        """Update a pet"""
        if pet_id > len(pets) - 1:
            abort(404)
        for attr, value in data.items():
            pets[pet_id][attr] = value
        return pets[pet_id]

    @app.output({}, status_code=204)
    def delete(self, pet_id):
        """Delete a pet"""
        if pet_id > len(pets) - 1:
            abort(404)
        pets[pet_id]['deleted'] = True
        pets[pet_id]['name'] = 'Ghost'
        return ''


class Pets(MethodView):

    @app.output(PetOut(many=True))
    def get(self):
        """Get all pets"""
        return pets

    @app.input(PetIn)
    @app.output(PetOut, status_code=201)
    def post(self, data):
        """Create a pet"""
        pet_id = len(pets)
        data['id'] = pet_id
        pets.append(data)
        return pets[pet_id]


app.add_url_rule('/', view_func=Hello.as_view('hello'))
app.add_url_rule('/pets/<int:pet_id>', view_func=Pet.as_view('pet'))
app.add_url_rule('/pets', view_func=Pets.as_view('pets'))
