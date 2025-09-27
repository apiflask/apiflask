import typing as t
from flask import current_app
from apiflask import APIFlask, APIKeyHeaderAuth, abort
from authlib.jose import jwt, JoseError

app = APIFlask(__name__)
auth = APIKeyHeaderAuth()
app.config['SECRET_KEY'] = 'secret-key'


class User:
    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username

    def get_apikey(self):
        header = {'alg': 'HS256'}
        payload = {'id': self.id}
        return jwt.encode(header, payload, current_app.config['SECRET_KEY']).decode()


users = [
    User(1, 'lorem'),
    User(2, 'ipsum'),
]


def get_user_by_id(id: int) -> t.Union[User, None]:
    return tuple(filter(lambda u: u.id == id, users))[0]


@auth.verify_token
def verify_apikey(apikey: str) -> t.Union[User, None]:
    try:
        data = jwt.decode(
            apikey.encode('ascii'),
            current_app.config['SECRET_KEY'],
        )
        id = data['id']
        user = get_user_by_id(id)
    except JoseError:
        return None
    except IndexError:
        return None
    return user


@app.post('/apikey/<int:id>')
def get_token(id: int):
    if get_user_by_id(id) is None:
        abort(404)
    return {'api_key': f'{get_user_by_id(id).get_apikey()}'}


@app.get('/name')
@app.auth_required(auth)
def get_username():
    return auth.current_user.username
