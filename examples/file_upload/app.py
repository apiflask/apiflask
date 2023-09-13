import os

from werkzeug.utils import secure_filename
from apiflask import APIFlask, Schema
from apiflask.fields import File, String

app = APIFlask(__name__)

upload_dir = './upload'


class Image(Schema):
    image = File()


class ProfileIn(Schema):
    name = String()
    avatar = File()


@app.post('/images')
@app.input(Image, location='files')
def upload_image(files_data):
    f = files_data['image']

    filename = secure_filename(f.filename)
    f.save(os.path.join(upload_dir, filename))

    return {'message': f'file {filename} saved.'}


@app.post('/profiles')
@app.input(ProfileIn, location='form_and_files')
def create_profile(form_and_files_data):
    avatar_file = form_and_files_data['avatar']
    name = form_and_files_data['name']

    avatar_filename = secure_filename(avatar_file.filename)
    avatar_file.save(os.path.join(upload_dir, avatar_filename))

    return {'message': f"{name}'s profile created."}
