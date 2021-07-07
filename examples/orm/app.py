from apiflask import APIFlask, Schema, input, output
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask_sqlalchemy import SQLAlchemy

app = APIFlask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class PetModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    category = db.Column(db.String(10))


@app.before_first_request
def init_database():
    db.create_all()

    pets = [
        {'name': 'Kitty', 'category': 'cat'},
        {'name': 'Coco', 'category': 'dog'},
        {'name': 'Flash', 'category': 'cat'}
    ]
    for pet_data in pets:
        pet = PetModel(**pet_data)
        db.session.add(pet)
    db.session.commit()


class PetInSchema(Schema):
    name = String(required=True, validate=Length(0, 10))
    category = String(required=True, validate=OneOf(['dog', 'cat']))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


@app.get('/')
def say_hello():
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@output(PetOutSchema)
def get_pet(pet_id):
    return PetModel.query.get_or_404(pet_id)


@app.get('/pets')
@output(PetOutSchema(many=True))
def get_pets():
    return PetModel.query.all()


@app.post('/pets')
@input(PetInSchema)
@output(PetOutSchema, 201)
def create_pet(data):
    pet = PetModel(**data)
    db.session.add(pet)
    db.session.commit()
    return pet


@app.patch('/pets/<int:pet_id>')
@input(PetInSchema(partial=True))
@output(PetOutSchema)
def update_pet(pet_id, data):
    pet = PetModel.query.get_or_404(pet_id)
    for attr, value in data.items():
        setattr(pet, attr, value)
    db.session.commit()
    return pet


@app.delete('/pets/<int:pet_id>')
@output({}, 204)
def delete_pet(pet_id):
    pet = PetModel.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return ''
