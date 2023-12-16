import io

import pytest
from marshmallow.exceptions import ValidationError
from werkzeug.datastructures import FileStorage

from apiflask import validators


def test_filesize_min():
    fs = FileStorage(io.BytesIO(b''.ljust(1024)))
    assert validators.FileSize(min='1 KiB', max='2 KiB')(fs) is fs
    assert validators.FileSize(min='0 KiB', max='1 KiB')(fs) is fs
    assert validators.FileSize()(fs) is fs
    assert validators.FileSize(min_inclusive=False, max_inclusive=False)(fs) is fs
    assert validators.FileSize(min='1 KiB', max='1 KiB')(fs) is fs

    with pytest.raises(ValidationError, match='Must be greater than or equal to 2 KiB'):
        validators.FileSize(min='2 KiB', max='3 KiB')(fs)
    with pytest.raises(ValidationError, match='Must be greater than or equal to 2 KiB'):
        validators.FileSize(min='2 KiB')(fs)
    with pytest.raises(ValidationError, match='Must be greater than 1 KiB'):
        validators.FileSize(min='1 KiB', max='2 KiB', min_inclusive=False, max_inclusive=True)(fs)
    with pytest.raises(ValidationError, match='less than 1 KiB'):
        validators.FileSize(min='1 KiB', max='1 KiB', min_inclusive=True, max_inclusive=False)(fs)


def test_filesize_max():
    fs = FileStorage(io.BytesIO(b''.ljust(2048)))
    assert validators.FileSize(min='1 KiB', max='2 KiB')(fs) is fs
    assert validators.FileSize(max='2 KiB')(fs) is fs
    assert validators.FileSize()(fs) is fs
    assert validators.FileSize(min_inclusive=False, max_inclusive=False)(fs) is fs
    assert validators.FileSize(min='2 KiB', max='2 KiB')(fs) is fs

    with pytest.raises(ValidationError, match='less than or equal to 1 KiB'):
        validators.FileSize(min='0 KiB', max='1 KiB')(fs)
    with pytest.raises(ValidationError, match='less than or equal to 1 KiB'):
        validators.FileSize(max='1 KiB')(fs)
    with pytest.raises(ValidationError, match='less than 2 KiB'):
        validators.FileSize(min='1 KiB', max='2 KiB', min_inclusive=True, max_inclusive=False)(fs)
    with pytest.raises(ValidationError, match='greater than 2 KiB'):
        validators.FileSize(min='2 KiB', max='2 KiB', min_inclusive=False, max_inclusive=True)(fs)


def test_filesize_repr():
    assert (
        repr(
            validators.FileSize(
                min=None, max=None, error=None, min_inclusive=True, max_inclusive=True
            )
        )
        == '<FileSize(min=None, max=None, min_inclusive=True, max_inclusive=True, error=None)>'
    )

    assert repr(
        validators.FileSize(
            min='1 KiB', max='3 KiB', error='foo', min_inclusive=False, max_inclusive=False
        )
    ) == "<FileSize(min='1 KiB', max='3 KiB', min_inclusive=False, max_inclusive=False, error='foo')>"  # noqa: E501


def test_filesize_wrongtype():
    with pytest.raises(TypeError, match='A FileStorage object is required, not '):
        validators.FileSize()(1)


def test_filetype():
    png_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.png')
    assert validators.FileType(['.png'])(png_fs) is png_fs
    assert validators.FileType(['.PNG'])(png_fs) is png_fs

    PNG_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.PNG')
    assert validators.FileType(['.png'])(PNG_fs) is PNG_fs
    assert validators.FileType(['.PNG'])(PNG_fs) is PNG_fs

    with pytest.raises(TypeError, match='A FileStorage object is required, not '):
        validators.FileType(['.png'])(1)

    with pytest.raises(
        ValidationError,
        match=r'Not an allowed file type. Allowed file types: \[.*?\]'  # noqa: W605
    ):
        jpg_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test.jpg')
        validators.FileType(['.png'])(jpg_fs)

    with pytest.raises(
        ValidationError,
        match=r'Not an allowed file type. Allowed file types: \[.*?\]'  # noqa: W605
    ):
        no_ext_fs = FileStorage(io.BytesIO(b''.ljust(1024)), 'test')
        validators.FileType(['.png'])(no_ext_fs)
