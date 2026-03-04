from __future__ import annotations

import typing as t

from flask import request
from flask import url_for
from pydantic import BaseModel
from werkzeug.http import HTTP_STATUS_CODES

from .schemas import PaginationModel
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


def pagination_builder(
    pagination: PaginationType,
    schema_type: t.Literal['marshmallow', 'pydantic'] = 'marshmallow',
    **kwargs: t.Any,
) -> dict | PaginationModel:
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

    With marshmallow
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
    def get_pets(query_data):
        pagination = PetModel.query.paginate(
            page=query_data['page'],
            per_page=query_data['per_page']
        )
        pets = pagination.items
        return {
            'pets': pets,
            'pagination': pagination_builder(pagination)
        }
    ```

    With Pydantic:
    ```python
    from apiflask import pagination_builder, PaginationModel
    from pydantic import BaseModel, Field, ConfigDict

    ...

    class PetQuery(BaseModel):
        page: int = Field(default=1)
        per_page: int = Field(default=20, le=30)


    class PetOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str
        category: str


    class PetsOut(BaseModel):
        pets: List[PetOut] = []
        pagination: PaginationModel


    @app.get('/pets')
    @app.input(PetQuery, location='query')
    @app.output(PetsOut)
    def get_pets(query_data: PetQuery):
        pagination = PetModel.query.paginate(
            page=query_data.page,
            per_page=query_data.per_page
        )
        pets = pagination.items
        return PetsOut(
            pets=pets,
            pagination=pagination_builder(pagination, schema_type='pydantic')
        )
    ```

    See <https://github.com/apiflask/apiflask/blob/main/examples/pagination/app.py>
    for the complete example.

    Arguments:
        pagination: The pagination object.
        schema_type: The pagination data type. One of `'marshmallow'`, `'pydantic'`.
        **kwargs: Additional keyword arguments that passed to the
            `url_for` function when generate the page-related URLs.

    *Version Added: 0.6.0*

    *Version Changed: 3.1.0*

    - Add `schema_type` parameter.
    """
    endpoint: str | None = request.endpoint
    per_page: int = pagination.per_page

    def get_page_url(page: int) -> str:
        if endpoint is None:  # pragma: no cover
            return ''
        return url_for(endpoint, page=page, per_page=per_page, _external=True, **kwargs)

    next: str = get_page_url(pagination.next_num) if pagination.has_next else ''
    prev: str = get_page_url(pagination.prev_num) if pagination.has_prev else ''
    pagination_dict = {
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
    if schema_type == 'marshmallow':
        return pagination_dict
    elif schema_type == 'pydantic':
        return PaginationModel(**pagination_dict)  # type: ignore
    else:
        raise ValueError('Invalid schema_type parameter, should be "marshmallow" or "pydantic"')


def _get_fields_by_type(model_class: type[BaseModel], field_type: type) -> t.List[str]:
    """A helper function to get the fields of the specified type in BaseModel.

    *Version Added: 3.1.0*
    """
    return [
        field_name
        for field_name, field in model_class.__pydantic_fields__.items()
        if field_type == field.annotation or field_type in t.get_args(field.annotation)
    ]
