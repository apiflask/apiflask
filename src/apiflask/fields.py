# Field aliases were skipped (e.g., Str, Int, Url, etc.)
import typing as t
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from flask_marshmallow.fields import AbsoluteURLFor as AbsoluteURLFor
    from flask_marshmallow.fields import Hyperlinks as Hyperlinks
    from flask_marshmallow.fields import URLFor as URLFor
from marshmallow.fields import AwareDateTime as AwareDateTime
from marshmallow.fields import Boolean as Boolean
from marshmallow.fields import Constant as Constant
from marshmallow.fields import Date as Date
from marshmallow.fields import DateTime as DateTime
from marshmallow.fields import Decimal as Decimal
from marshmallow.fields import Dict as Dict
from marshmallow.fields import Email as Email
from marshmallow.fields import Field as Field
from marshmallow.fields import Float as Float
from marshmallow.fields import Function as Function
from marshmallow.fields import Integer as Integer
from marshmallow.fields import IP as IP
from marshmallow.fields import IPv4 as IPv4
from marshmallow.fields import IPv6 as IPv6
from marshmallow.fields import List as List
from marshmallow.fields import Mapping as Mapping
from marshmallow.fields import Method as Method
from marshmallow.fields import NaiveDateTime as NaiveDateTime
from marshmallow.fields import Nested as Nested
from marshmallow.fields import Number as Number
from marshmallow.fields import Pluck as Pluck
from marshmallow.fields import Raw as Raw
from marshmallow.fields import String as String
from marshmallow.fields import Time as Time
from marshmallow.fields import TimeDelta as TimeDelta
from marshmallow.fields import Tuple as Tuple
from marshmallow.fields import URL as URL
from marshmallow.fields import UUID as UUID
from marshmallow.fields import Enum as Enum
from webargs.fields import DelimitedList as DelimitedList
from webargs.fields import DelimitedTuple as DelimitedTuple


class File(Field):
    """A binary file field, it should only be used in an input schema.

    Examples:

    ```python
    import os

    from werkzeug.utils import secure_filename
    from apiflask.fields import File


    class Image(Schema):
        image = File()


    @app.post('/images')
    @app.input(Image, location='files')
    def upload_image(files_data):
        f = files_data['image']
        # use `secure_filename` to clean the filename, notice it will only keep ascii characters
        filename = secure_filename(f.filename)
        f.save(os.path.join(the_path_to_uploads, filename))

        return {'message': f'file {filename} saved.'}
    ```
    The file object is an instance of `werkzeug.datastructures.FileStorage`, see more details in the
    [docs](https://werkzeug.palletsprojects.com/datastructures/#werkzeug.datastructures.FileStorage).  # noqa: B950, E501

    Use `form_and_files` location if you want to put both files
    and other normal fields in one schema.

    ```python
    import os

    from werkzeug.utils import secure_filename
    from apiflask.fields import String, File


    class ProfileIn(Schema):
        name = String()
        avatar = File()

    @app.post('/profiles')
    @app.input(ProfileIn, location='form_and_files')
    def create_profile(form_and_files_data):
        avatar_file = form_and_files_data['avatar']
        name = form_and_files_data['name']

        # use `secure_filename` to clean the filename, notice it will only keep ascii characters
        avatar_filename = secure_filename(avatar_file.filename)
        avatar_file.save(os.path.join(the_path_to_uploads, avatar_filename))

        profile = Profile(name=name, avatar_filename=avatar_filename)
        # ...
        return {'message': 'profile created.'}
    ```

    In the current implementation, `files` location data will also include
    the form data (equals to `form_and_files`).

    *Version Added: 1.0*

    This field accepts the same keyword arguments that `Field` receives.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata['type'] = 'string'
        self.metadata['format'] = 'binary'

    default_error_messages: t.Dict[str, str] = {
        'invalid': 'Not a valid file.'
    }

    def _deserialize(self, value, attr, data, **kwargs) -> t.Any:
        from werkzeug.datastructures import FileStorage
        if not isinstance(value, FileStorage):
            raise self.make_error('invalid')
        return value


class Config(Field):
    """A field for Flask configuration values.

    Examples:

    ```python
    from apiflask import APIFlask, Schema
    from apiflask.fields import String, Config

    app = APIFlask(__name__)
    app.config['API_TITLE'] = 'Pet API'

    class FooSchema(Schema):
        user = String()
        title = Config('API_TITLE')

    @app.get('/foo')
    @app.output(FooSchema)
    def foo():
        return {'user': 'test'}
    ```

    This field should only be used in an output schema. The `ValueError` will
    be raised if the config key is not found in the app config.

    *Version Added: 2.0.1*
    """

    _CHECK_ATTRIBUTE = False

    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key

    def _serialize(self, value, attr, obj, **kwargs) -> t.Any:
        from flask import current_app
        if self.key not in current_app.config:
            raise ValueError(f'The key {self.key} is not found in the app config.')
        return current_app.config[self.key]
