import os
import sys
from importlib import reload

import pytest

full_examples = [
    'basic',
    'orm',
    'cbv',
    'openapi',
    'blueprint_tags',
    'base_response',
    'dataclass',
]

examples = full_examples + [
    'pagination'
]


@pytest.fixture
def client(request):
    app_path = os.path.join(os.path.dirname(__file__), f'{request.param}')
    sys.path.insert(0, app_path)
    import app
    app = reload(app)
    _app = app.app
    _app.testing = True
    sys.path.remove(app_path)
    client = _app.test_client()
    client._example = request.param
    return client


@pytest.mark.parametrize('client', examples, indirect=True)
def test_say_hello(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.json
    if client._example == 'base_response':
        data = rv.json['data']
    else:
        data = rv.json
    assert data['message'] == 'Hello!'


@pytest.mark.parametrize('client', examples, indirect=True)
def test_get_pet(client):
    rv = client.get('/pets/1')
    assert rv.status_code == 200
    assert rv.json
    if client._example == 'base_response':
        data = rv.json['data']
    else:
        data = rv.json
    if client._example == 'orm':
        assert data['name'] == 'Kitty'
        assert data['category'] == 'cat'
    elif client._example == 'pagination':
        assert data['name'] == 'Pet 1'
    else:
        assert data['name'] == 'Coco'
        assert data['category'] == 'dog'

    rv = client.get('/pets/13')
    if client._example != 'pagination':
        assert rv.status_code == 404
        assert rv.json


@pytest.mark.parametrize('client', full_examples, indirect=True)
def test_get_pets(client):
    rv = client.get('/pets')
    assert rv.status_code == 200
    assert rv.json
    if client._example == 'base_response':
        data = rv.json['data']
    else:
        data = rv.json
    assert len(rv.json) == 3
    assert data[0]['name'] == 'Kitty'
    assert data[0]['category'] == 'cat'


@pytest.mark.parametrize('client', full_examples, indirect=True)
def test_create_pet(client):
    rv = client.post('/pets', json={
        'name': 'Grey',
        'category': 'cat'
    })
    assert rv.status_code == 201
    assert rv.json
    if client._example == 'base_response':
        data = rv.json['data']
    else:
        data = rv.json
    assert data['name'] == 'Grey'
    assert data['category'] == 'cat'


@pytest.mark.parametrize('client', full_examples, indirect=True)
@pytest.mark.parametrize('data', [
    {'name': 'Grey', 'category': 'human'},
    {'name': 'Fyodor Mikhailovich Dostoevsky', 'category': 'cat'},
    {'category': 'cat'},
    {'name': 'Grey'}
])
def test_create_pet_with_bad_data(client, data):
    rv = client.post('/pets', json=data)
    assert rv.status_code == 400
    assert rv.json


@pytest.mark.parametrize('client', full_examples, indirect=True)
def test_update_pet(client):
    new_data = {
        'name': 'Ghost',
        'category': 'dog'
    }

    rv = client.patch('/pets/1', json=new_data)
    assert rv.status_code == 200
    assert rv.json

    rv = client.get('/pets/1')
    assert rv.status_code == 200
    if client._example == 'base_response':
        data = rv.json['data']
    else:
        data = rv.json
    assert data['name'] == new_data['name']
    assert data['category'] == new_data['category']

    rv = client.patch('/pets/13', json=new_data)
    assert rv.status_code == 404
    assert rv.json


@pytest.mark.parametrize('client', full_examples, indirect=True)
@pytest.mark.parametrize('data', [
    {'name': 'Fyodor Mikhailovich Dostoevsky'},
    {'category': 'human'}
])
def test_update_pet_with_bad_data(client, data):
    rv = client.patch('/pets/1', json=data)
    assert rv.status_code == 400
    assert rv.json


@pytest.mark.parametrize('client', full_examples, indirect=True)
def test_delete_pet(client):
    rv = client.delete('/pets/1')
    assert rv.status_code == 204

    rv = client.get('/pets/1')
    assert rv.status_code == 404
    assert rv.json

    rv = client.delete('/pets/13')
    assert rv.status_code == 404
    assert rv.json


@pytest.mark.parametrize('client', ['pagination'], indirect=True)
def test_get_pets_pagination(client):
    rv = client.get('/pets')
    assert rv.status_code == 200
    assert rv.json
    assert 'pets' in rv.json
    assert 'pagination' in rv.json
    assert len(rv.json['pets']) == 20
    assert rv.json['pagination']['per_page'] == 20
    assert rv.json['pagination']['pages'] == 5
    assert rv.json['pagination']['total'] == 100
    assert rv.json['pagination']['page'] == 1
    assert rv.json['pets'][0]['id'] == 1
    assert rv.json['pets'][-1]['id'] == 20

    per_page = 10
    page = 2
    rv = client.get(f'/pets?per_page={per_page}&page={page}')
    assert rv.status_code == 200
    assert rv.json
    assert 'pets' in rv.json
    assert 'pagination' in rv.json
    assert len(rv.json['pets']) == per_page
    assert rv.json['pagination']['per_page'] == per_page
    assert rv.json['pagination']['pages'] == 10
    assert rv.json['pets'][0]['id'] == 11
    assert rv.json['pets'][-1]['id'] == 20


@pytest.mark.parametrize('client', ['pagination'], indirect=True)
def test_get_pets_pagination_with_bad_data(client):
    rv = client.get('/pets?per_page=100')
    assert rv.status_code == 400

    rv = client.get('/pets?page=100')
    assert rv.status_code == 404
