import typing as t

from flask import current_app
from apiflask import APIFlask, HTTPBasicAuth, HTTPTokenAuth, MultiAuth, Schema, abort
from werkzeug.security import generate_password_hash, check_password_hash
from apiflask.fields import String
from authlib.jose import jwt, JoseError

app = APIFlask(__name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
multi_auth = MultiAuth(basic_auth, token_auth)
app.config['SECRET_KEY'] = 'secret-key'


class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = generate_password_hash(password)

    def get_token(self):
        header = {'alg': 'HS256'}
        payload = {'id': self.id}
        return jwt.encode(header, payload, current_app.config['SECRET_KEY']).decode()


users = [
    User(1, 'lorem', 'foo'),
    User(2, 'ipsum', 'bar'),
]

username_map = {user.username: user for user in users}


def get_user_by_id(id: int) -> t.Union[User, None]:
    return tuple(filter(lambda u: u.id == id, users))[0]


@basic_auth.verify_password
def verify_password(username: str, password: str) -> t.Union[User, None]:
    if username in username_map and check_password_hash(username_map[username].password, password):
        return username_map[username]
    return None


@token_auth.verify_token
def verify_token(token: str) -> t.Union[User, None]:
    try:
        data = jwt.decode(
            token.encode('ascii'),
            current_app.config['SECRET_KEY'],
        )
        id = data['id']
        user = get_user_by_id(id)
    except JoseError:
        return None
    except IndexError:
        return None
    return user


class Token(Schema):
    token = String()


@app.post('/token/<int:id>')
@app.output(Token)
def get_token(id: int):
    if get_user_by_id(id) is None:
        abort(404)
    return {'token': f'Bearer {get_user_by_id(id).get_token()}'}


@app.route('/')
@app.auth_required(multi_auth)
def index():
    return f'Hello, {multi_auth.current_user.username}'
