import os
from typing import Annotated

from werkzeug.utils import secure_filename
from apiflask.fields import UploadFile
from apiflask.validators import validate_file_size
from apiflask.validators import validate_file_type
from apiflask import APIFlask
from pydantic import AfterValidator
from pydantic import BaseModel


app = APIFlask(__name__)
upload_dir = '../upload'


class Image(BaseModel):
    image: Annotated[
        UploadFile,
        AfterValidator(validate_file_type(['.png', '.jpg', '.jpeg', '.gif'])),
        AfterValidator(validate_file_size(max='5 MB')),
    ]


class ProfileIn(BaseModel):
    name: str
    avatar: Annotated[
        UploadFile,
        AfterValidator(validate_file_type(['.png', '.jpg', '.jpeg'])),
        AfterValidator(validate_file_size(max='2 MB')),
    ]


@app.post('/images')
@app.input(Image, location='files')
def upload_image(files_data: Image):
    f = files_data.image

    filename = secure_filename(f.filename)
    f.save(os.path.join(upload_dir, filename))

    return {'message': f'file {filename} saved.'}


@app.post('/profiles')
@app.input(ProfileIn, location='form_and_files')
def create_profile(form_and_files_data: ProfileIn):
    avatar_file = form_and_files_data.avatar
    name = form_and_files_data.name

    avatar_filename = secure_filename(avatar_file.filename)
    avatar_file.save(os.path.join(upload_dir, avatar_filename))

    return {'message': f"{name}'s profile created."}
