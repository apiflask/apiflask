import io
import typing as t

import pytest
from pydantic import AfterValidator
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage

from apiflask.fields import UploadFile
from apiflask.validators import validate_file_size
from apiflask.validators import validate_file_type


def test_validate_file_type():
    class PngUploadFileModel(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_type(['.png']))]

    class PNGUploadFileModel(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_type(['.PNG']))]

    png_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.png')
    assert PngUploadFileModel(file=png_fs).file is png_fs
    assert PNGUploadFileModel(file=png_fs).file is png_fs

    PNG_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.PNG')
    assert PngUploadFileModel(file=PNG_fs).file is PNG_fs
    assert PNGUploadFileModel(file=PNG_fs).file is PNG_fs

    jpg_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.jpg')
    with pytest.raises(ValueError, match=r'Not an allowed file type. Allowed file types: \[.*?\]'):
        PngUploadFileModel(file=jpg_fs)

    no_ext_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test')
    with pytest.raises(ValueError, match=r'Not an allowed file type. Allowed file types: \[.*?\]'):
        PngUploadFileModel(file=no_ext_fs)


def test_validate_file_size():
    class UploadFileModel1(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_size())]

    class UploadFileModel2(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_size(min='1 KiB', max='2 KiB'))]

    class UploadFileModel3(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_size(min='0 KiB', max='1 KiB'))]

    class UploadFileModel4(BaseModel):
        file: t.Annotated[UploadFile, AfterValidator(validate_file_size(min='1 KiB', max='1 KiB'))]

    class UploadFileModel5(BaseModel):
        file: t.Annotated[
            UploadFile, AfterValidator(validate_file_size(min_inclusive=False, max_inclusive=False))
        ]

    fs = FileStorage(io.BytesIO(b''.ljust(1024)))
    assert UploadFileModel1(file=fs).file is fs
    assert UploadFileModel2(file=fs).file is fs
    assert UploadFileModel3(file=fs).file is fs
    assert UploadFileModel4(file=fs).file is fs
    assert UploadFileModel5(file=fs).file is fs

    with pytest.raises(ValueError, match=r'Must be greater than or equal to 2 KiB'):

        class UploadFileModel6(BaseModel):
            file: t.Annotated[
                UploadFile, AfterValidator(validate_file_size(min='2 KiB', max='3 KiB'))
            ]

        UploadFileModel6(file=fs)

    with pytest.raises(ValueError, match=r'Must be greater than or equal to 2 KiB'):

        class UploadFileModel7(BaseModel):
            file: t.Annotated[UploadFile, AfterValidator(validate_file_size(min='2 KiB'))]

        UploadFileModel7(file=fs)

    with pytest.raises(ValueError, match=r'Must be greater than 1 KiB'):

        class UploadFileModel8(BaseModel):
            file: t.Annotated[
                UploadFile,
                AfterValidator(
                    validate_file_size(
                        min='1 KiB', max='2 KiB', min_inclusive=False, max_inclusive=True
                    )
                ),
            ]

        UploadFileModel8(file=fs)

    with pytest.raises(ValueError, match=r'less than 1 KiB'):

        class UploadFileModel8(BaseModel):
            file: t.Annotated[
                UploadFile,
                AfterValidator(
                    validate_file_size(
                        min='1 KiB', max='1 KiB', min_inclusive=True, max_inclusive=False
                    )
                ),
            ]

        UploadFileModel8(file=fs)
