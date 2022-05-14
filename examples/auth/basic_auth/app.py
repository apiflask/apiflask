import typing as t

from apiflask import APIFlask, HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = APIFlask(__name__)
auth = HTTPBasicAuth()

users = {
    'userA': generate_password_hash('foo'),
    'userB': generate_password_hash('bar'),
}


@auth.verify_password
def verify_password(username: str, password: str) -> t.Union[str, None]:
    if (
        username in users
        and check_password_hash(users[username], password)
    ):
        return username
    return None


@app.route('/')
@app.auth_required(auth)
def index():
    return f'Hello, {auth.current_user}'
