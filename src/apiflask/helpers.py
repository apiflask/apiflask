import re
import typing as t

from flask import request
from flask import url_for
from werkzeug.datastructures import FileStorage
from werkzeug.http import HTTP_STATUS_CODES

from .types import PaginationType


_sentinel = object()


def get_reason_phrase(status_code: int, default: str = 'Unknown') -> str:
    """A helper function to get the reason phrase of the given status code.

    Arguments:
        status_code: A standard HTTP status code.
        default: The default phrase to use if not found, defaults to "Unknown".

    *Version Changed: 0.6.0*

    - Add `default` parameter.
    """
    return HTTP_STATUS_CODES.get(status_code, default)


def pagination_builder(pagination: PaginationType, **kwargs: t.Any) -> dict:
    """A helper function to make pagination data.

    This function is designed based on Flask-SQLAlchemy's `Pagination` class.
    If you are using a different or custom pagination class, make sure the
    passed pagination object has the following attributes:

    - page
    - per_page
    - pages
    - total
    - next_num
    - has_next
    - prev_num
    - has_prev

    Or you can write your own builder function to build the pagination data.

    Examples:

    ```python
    from apiflask import PaginationSchema, pagination_builder

    ...

    class PetQuery(Schema):
        page = Integer(load_default=1)
        per_page = Integer(load_default=20, validate=Range(max=30))


    class PetsOut(Schema):
        pets = List(Nested(PetOut))
        pagination = Nested(PaginationSchema)


    @app.get('/pets')
    @app.input(PetQuery, location='query')
    @app.output(PetsOut)
    def get_pets(query):
        pagination = PetModel.query.paginate(
            page=query['page'],
            per_page=query['per_page']
        )
        pets = pagination.items
        return {
            'pets': pets,
            'pagination': pagination_builder(pagination)
        }
    ```

    See <https://github.com/apiflask/apiflask/blob/main/examples/pagination/app.py>
    for the complete example.

    Arguments:
        pagination: The pagination object.
        **kwargs: Additional keyword arguments that passed to the
            `url_for` function when generate the page-related URLs.

    *Version Added: 0.6.0*
    """
    endpoint: t.Optional[str] = request.endpoint
    per_page: int = pagination.per_page

    def get_page_url(page: int) -> str:
        if endpoint is None:  # pragma: no cover
            return ''
        return url_for(
            endpoint, page=page, per_page=per_page, _external=True, **kwargs
        )

    next: str = get_page_url(pagination.next_num) if pagination.has_next else ''
    prev: str = get_page_url(pagination.prev_num) if pagination.has_prev else ''
    return {
        'total': pagination.total,
        'pages': pagination.pages,
        'per_page': per_page,
        'page': pagination.page,
        'next': next,
        'prev': prev,
        'first': get_page_url(1),
        'last': get_page_url(pagination.pages),
        'current': get_page_url(pagination.page),
    }


def get_filestorage_size(file: FileStorage) -> int:
    """A helper function to get the size of the FileStorage object in bytes.

    Arguments:
        file: A FileStorage object.

    *Version added: 2.1.0*
    """
    size = len(file.read())
    file.stream.seek(0)
    return size


# This helper function is copied from loguru with few modifications.
# https://github.com/Delgan/loguru/blob/master/loguru/_string_parsers.py#L35
def parse_size(size: str) -> float:  # noqa: E302
    """A helper function to parse a str representing the size into a number in bytes.

    Arguments:
        size: A str representing the size.

    *Version added: 2.1.0*
    """
    size = size.strip()
    reg = re.compile(r'([e\+\-\.\d]+)\s*([kmgtpezy])?(i)?(b)', flags=re.I)

    match = reg.fullmatch(size)

    if not match:
        raise ValueError(f"Invalid size value: '{size!r}'")

    s, u, i, b = match.groups()

    try:
        s = float(s)
    except ValueError as e:
        raise ValueError(f"Invalid float value while parsing size: '{s!r}'") from e

    u = 'kmgtpezy'.index(u.lower()) + 1 if u else 0
    i = 1024 if i else 1000
    b = {'b': 8, 'B': 1}[b] if b else 1
    size: float = s * i**u / b

    return size
