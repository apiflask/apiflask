import typing as t
from flask import current_app, g
from apiflask import APIFlask, HTTPTokenAuth, abort
from authlib.jose import jwt

app = APIFlask(__name__)
auth = HTTPTokenAuth()
app.config['SECRET_KEY'] = 'secret-key'


class User:
    def __init__(self, id: int, secret: str):
        self.id = id
        self.secret = secret

    def get_token(self):
        header = {'alg': 'HS256'}
        payload = {
            id: self.id
        }
        return jwt.encode(
            header, payload, current_app.config['SECRET_KEY']
        ).decode()


users = [
    User(1, "lorem"),
    User(2, "ipsum"),
    User(3, "test"),
]


def get_user_by_id(id: int) -> t.Union[User, None]:
    return tuple(filter(lambda u: u.id == id, users))[0]


@auth.verify_token
def verify_token(token: str) -> t.Union[User, None]:
    try:
        data = jwt.decode(
            token.encode("ascii"),
            current_app.config['SECRET_KEY'],
        )
        id = data['id']
    except BaseException:
        return None
    user = get_user_by_id(id)
    g.current_user = user
    return user


@app.post("/token/<int:id>")
def get_token(id: int):
    if get_user_by_id(id) is None:
        abort(404)
    return {
        'token': f'Bearer {get_user_by_id(id).get_token()}'
    }


@app.get("/name/<int:id>")
@auth.login_required
def get_secret():
    if isinstance(g.current_user, User):
        return g.current_user.secret
    abort(401)
