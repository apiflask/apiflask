from marshmallow.exceptions import ValidationError
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

from .helpers import get_filestorage_size
from .helpers import parse_size


class FileSize(Validator):
    """Validator which succeeds if the file passed to it is within the specified
    size range. If ``min`` is not specified, or is specified as `None`,
    no lower bound exists. If ``max`` is not specified, or is specified as `None`,
    no upper bound exists. The inclusivity of the bounds (if they exist) is configurable.
    If ``min_inclusive`` is not specified, or is specified as `True`, then
    the ``min`` bound is included in the range. If ``max_inclusive`` is not specified,
    or is specified as `True`, then the ``max`` bound is included in the range.

    :param min: The minimum size (lower bound). If not provided, minimum
        size will not be checked.
    :param max: The maximum size (upper bound). If not provided, maximum
        size will not be checked.
    :param min_inclusive: Whether the `min` bound is included in the range.
    :param max_inclusive: Whether the `max` bound is included in the range.
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}`, `{min}` and `{max}`.
    """

    message_min = 'Must be {min_op} {{min}}.'
    message_max = 'Must be {max_op} {{max}}.'
    message_all = 'Must be {min_op} {{min}} and {max_op} {{max}}.'

    message_gte = 'greater than or equal to'
    message_gt = 'greater than'
    message_lte = 'less than or equal to'
    message_lt = 'less than'

    def __init__(
        self,
        min: str | None = None,
        max: str | None = None,
        min_inclusive: bool = True,
        max_inclusive: bool = True,
        error: str | None = None,
    ) -> None:
        self.min = min
        self.max = max
        self.min_size = parse_size(self.min) if self.min else None
        self.max_size = parse_size(self.max) if self.max else None
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive
        self.error = error

        self.message_min = self.message_min.format(
            min_op=self.message_gte if self.min_inclusive else self.message_gt
        )
        self.message_max = self.message_max.format(
            max_op=self.message_lte if self.max_inclusive else self.message_lt
        )
        self.message_all = self.message_all.format(
            min_op=self.message_gte if self.min_inclusive else self.message_gt,
            max_op=self.message_lte if self.max_inclusive else self.message_lt,
        )

    def _repr_args(self) -> str:
        return 'min={!r}, max={!r}, min_inclusive={!r}, max_inclusive={!r}'.format(
            self.min, self.max, self.min_inclusive, self.max_inclusive
        )

    def _format_error(self, value: FileStorage, message: str) -> str:
        return (self.error or message).format(input=value, min=self.min, max=self.max)

    def __call__(self, value: FileStorage) -> FileStorage:
        if not isinstance(value, FileStorage):
            raise TypeError(
                f"a FileStorage object is required, not '{type(value).__name__!r}'"
            )

        file_size = get_filestorage_size(value)
        if self.min_size is not None and (
            file_size < self.min_size if self.min_inclusive else file_size <= self.min_size
        ):
            message = self.message_min if self.max is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        if self.max_size is not None and (
            file_size > self.max_size if self.max_inclusive else file_size >= self.max_size
        ):
            message = self.message_max if self.min is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        return value
