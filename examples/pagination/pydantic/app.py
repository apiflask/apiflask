import random
from typing import List

from flask_sqlalchemy import SQLAlchemy
from apiflask import APIFlask, pagination_builder, PaginationModel
from pydantic import BaseModel, Field, ConfigDict

app = APIFlask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class PetModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    category = db.Column(db.String(10))


def init_database():
    db.create_all()
    for i in range(1, 101):
        name = f'Pet {i}'
        category = random.choice(['dog', 'cat'])
        pet = PetModel(name=name, category=category)
        db.session.add(pet)
    db.session.commit()


class PetQuery(BaseModel):
    page: int = Field(default=1)
    per_page: int = Field(default=20, le=30)


class PetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str


class PetsOut(BaseModel):
    pets: List[PetOut] = []
    pagination: PaginationModel


@app.get('/')
def say_hello():
    return {'message': 'Hello!'}


@app.get('/pets/<int:pet_id>')
@app.output(PetOut)
def get_pet(pet_id):
    return db.get_or_404(PetModel, pet_id)


@app.get('/pets')
@app.input(PetQuery, location='query')
@app.output(PetsOut)
def get_pets(query_data: PetQuery):
    pagination = db.paginate(
        db.select(PetModel), page=query_data.page, per_page=query_data.per_page
    )
    pets = pagination.items
    return {'pets': pets, 'pagination': pagination_builder(pagination, schema_type='pydantic')}


with app.app_context():
    init_database()
