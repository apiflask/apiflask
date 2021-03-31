from typing import Optional, Union
from flask import Blueprint

from .utils import route_shortcuts
from .utils import _sentinel


@route_shortcuts
class APIBlueprint(Blueprint):
    """Flask's `Blueprint` object with some web API support.

    Examples:

    ```python
    from apiflask import APIBlueprint

    bp = APIBlueprint(__name__, 'foo')
    ```

    *Version added: 0.2.0*
    """

    def __init__(
        self,
        name: str,
        import_name: str,
        tag: Optional[Union[str, dict]] = None,
        static_folder: Optional[str] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        url_defaults: Optional[dict] = None,
        root_path: Optional[str] = None,
        cli_group: Union[Optional[str]] = _sentinel  # type: ignore
    ) -> None:
        """Make a blueprint instance.

        Arguments:
            name: The name of the blueprint. Will be prepended to
                each endpoint name.
            import_name: The name of the blueprint package, usually
                `__name__`. This helps locate the `root_path` for the
                blueprint.
            tag: The tag of this blueprint. If not set, the
                `<blueprint name>.title()` will be used (`'foo'` -> `'Foo'`).
                Accepts a tag name string or an OpenAPI tag dict.
                Example:

                ```python
                bp = APIBlueprint(__name__, 'foo', tag='Foo')
                ```

                ```python
                bp = APIBlueprint(__name__, 'foo', tag={'name': 'Foo'})
                ```

        Other keyword arguments are directly pass to `flask.Blueprint`.
        """
        super(APIBlueprint, self).__init__(
            name,
            import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            url_prefix=url_prefix,
            subdomain=subdomain,
            url_defaults=url_defaults,
            root_path=root_path,
            cli_group=cli_group,
        )
        self.tag = tag
