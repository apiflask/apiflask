import typing as t
from flask import current_app
from apiflask import APIFlask, HTTPTokenAuth, Schema, abort
from apiflask.fields import String
from authlib.jose import jwt, JoseError

# app = APIFlask(__name__)

app = APIFlask(
    'My-App',
    docs_oauth2_redirect_path='/login/callback',
    docs_oauth2_redirect_path_external=True,
    docs_ui='swagger-ui',
)
oauth2 = {
    'type': 'oauth2',
    'flows': {
        'implicit': {
            'authorizationUrl': 'https://my-domain.okta.com/oauth2/default/v1/authorize',
            'scopes': {},
        }
    },
}
security_schemes = {
    'oauth2': oauth2,
}
app.security_schemes = security_schemes
app.config['SWAGGER_UI_OAUTH_CONFIG'] = {
    'clientId': '123abc',
    'scopes': 'openid',
    'additionalQueryStringParams': {
        'nonce': '123',
    },
}
app.config['SERVERS'] = [
    {'name': 'Prod', 'url': 'https://my-domain.com'},
    {'name': 'Dev', 'url': 'https://dev.my-domain.com'},
]
auth = HTTPTokenAuth()
app.config['SECRET_KEY'] = 'secret-key'


class User:
    def __init__(self, id: int, secret: str):
        self.id = id
        self.secret = secret

    def get_token(self):
        header = {'alg': 'HS256'}
        payload = {'id': self.id}
        return jwt.encode(header, payload, current_app.config['SECRET_KEY']).decode()


users = [
    User(1, 'lorem'),
    User(2, 'ipsum'),
    User(3, 'test'),
]


def get_user_by_id(id: int) -> t.Union[User, None]:
    return tuple(filter(lambda u: u.id == id, users))[0]


@auth.verify_token
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


@app.get('/name/<int:id>')
@app.auth_required(auth)
def get_secret(id):
    return auth.current_user.secret
