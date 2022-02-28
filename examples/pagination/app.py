import random

from flask_sqlalchemy import SQLAlchemy
from apiflask import APIFlask, Schema, PaginationSchema, pagination_builder
from apiflask.fields import Integer, String, List, Nested
from apiflask.validators import Range

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
    for i in range(1, 101):
        name = f'Pet {i}'
        category = random.choice(['dog', 'cat'])
        pet = PetModel(name=name, category=category)
        db.session.add(pet)
    db.session.commit()


class PetQuerySchema(Schema):
    page = Integer(load_default=1)
    per_page = Integer(load_default=20, validate=Range(max=30))


class PetOutSchema(Schema):
    id = Integer()
    name = String()
    category = String()


class PetsOutSchema(Schema):
    pets = List(Nested(PetOutSchema))
    pagination = Nested(PaginationSchema)


@app.get('/')
def say_hello():
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@app.output(PetOutSchema)
def get_pet(pet_id):
    return PetModel.query.get_or_404(pet_id)


@app.get('/pets')
@app.input(PetQuerySchema, 'query')
@app.output(PetsOutSchema)
def get_pets(query):
    pagination = PetModel.query.paginate(
        page=query['page'],
        per_page=query['per_page']
    )
    pets = pagination.items
    return {
        'pets': pets,
        'pagination': pagination_builder(pagination)
    }
