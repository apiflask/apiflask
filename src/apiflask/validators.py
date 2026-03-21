import os
import typing as t

from flask_marshmallow.validate import _get_filestorage_size
from flask_marshmallow.validate import _parse_size
from flask_marshmallow.validate import FileSize as FileSize
from flask_marshmallow.validate import FileType as FileType
from marshmallow.validate import ContainsNoneOf as ContainsNoneOf
from marshmallow.validate import ContainsOnly as ContainsOnly
from marshmallow.validate import Email as Email
from marshmallow.validate import Equal as Equal
from marshmallow.validate import Length as Length
from marshmallow.validate import NoneOf as NoneOf
from marshmallow.validate import OneOf as OneOf
from marshmallow.validate import Predicate as Predicate
from marshmallow.validate import Range as Range
from marshmallow.validate import Regexp as Regexp
from marshmallow.validate import URL as URL
from marshmallow.validate import Validator as Validator
from werkzeug.datastructures import FileStorage


def validate_file_type(
    accept: t.Iterable[str], error: t.Optional[str] = None
) -> t.Callable[[FileStorage], FileStorage]:
    """Validator which succeeds if the uploaded file is allowed by a given list
    of extensions.

    Example: ::

        class UploadFileModel(BaseModel):
            file: t.Annotated[UploadFile, AfterValidator(validate_file_type(['.png']))]

    :param accept: A sequence of allowed extensions.
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with ``{input}`` and ``{extensions}``.

     *Version Added: 3.1.0*
    """

    default_message = 'Not an allowed file type. Allowed file types: [{extensions}]'
    allowed_types = {ext.lower() for ext in accept}

    def _format_error(value: FileStorage) -> str:
        return (error or default_message).format(input=value, extensions=','.join(allowed_types))

    def validator(value: FileStorage) -> FileStorage:
        _, extension = os.path.splitext(value.filename) if value.filename else (None, None)
        if extension is None or extension.lower() not in allowed_types:
            raise ValueError(_format_error(value))
        return value

    return validator


def validate_file_size(
    min: t.Optional[str] = None,
    max: t.Optional[str] = None,
    min_inclusive: bool = True,
    max_inclusive: bool = True,
    error: t.Optional[str] = None,
) -> t.Callable[[FileStorage], FileStorage]:
    """Validator which succeeds if the file passed to it is within the specified
    size range. If ``min`` is not specified, or is specified as `None`,
    no lower bound exists. If ``max`` is not specified, or is specified as `None`,
    no upper bound exists. The inclusivity of the bounds (if they exist)
    is configurable.
    If ``min_inclusive`` is not specified, or is specified as `True`, then
    the ``min`` bound is included in the range. If ``max_inclusive`` is not specified,
    or is specified as `True`, then the ``max`` bound is included in the range.

    Example: ::

        class UploadFileModel(BaseModel):
            file: t.Annotated[
                UploadFile,
                AfterValidator(validate_file_size(min="1 KiB", max="2 KiB"))
            ]

    :param min: The minimum size (lower bound). If not provided, minimum
        size will not be checked.
    :param max: The maximum size (upper bound). If not provided, maximum
        size will not be checked.
    :param min_inclusive: Whether the ``min`` bound is included in the range.
    :param max_inclusive: Whether the ``max`` bound is included in the range.
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}`, `{min}` and `{max}`.

     *Version Added: 3.1.0*
    """

    message_min_tpl = 'Must be {min_op} {{min}}.'
    message_max_tpl = 'Must be {max_op} {{max}}.'
    message_all_tpl = 'Must be {min_op} {{min}} and {max_op} {{max}}.'

    message_gte = 'greater than or equal to'
    message_gt = 'greater than'
    message_lte = 'less than or equal to'
    message_lt = 'less than'

    message_min = message_min_tpl.format(min_op=message_gte if min_inclusive else message_gt)
    message_max = message_max_tpl.format(max_op=message_lte if max_inclusive else message_lt)
    message_all = message_all_tpl.format(
        min_op=message_gte if min_inclusive else message_gt,
        max_op=message_lte if max_inclusive else message_lt,
    )

    def _format_error(value: FileStorage, message: str) -> str:
        return (error or message).format(input=value, min=min, max=max)

    def validator(value: FileStorage) -> FileStorage:
        min_size = _parse_size(min) if min else None
        max_size = _parse_size(max) if max else None

        file_size = _get_filestorage_size(value)
        if min_size is not None and (
            file_size < min_size if min_inclusive else file_size <= min_size
        ):
            message = message_min if max is None else message_all
            raise ValueError(_format_error(value, message))

        if max_size is not None and (
            file_size > max_size if max_inclusive else file_size >= max_size
        ):
            message = message_max if min is None else message_all
            raise ValueError(_format_error(value, message))

        return value

    return validator
