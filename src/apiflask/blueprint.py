import typing as t

from flask import Blueprint

from .helpers import _sentinel
from .route import route_patch
from .route import route_shortcuts


@route_patch
@route_shortcuts
class APIBlueprint(Blueprint):
    """Flask's `Blueprint` object with some web API support.

    Examples:

    ```python
    from apiflask import APIBlueprint

    bp = APIBlueprint(__name__, 'foo')
    ```

    *Version changed: 0.5.0*

    - Add `enable_openapi` parameter.

    *Version added: 0.2.0*
    """

    def __init__(
        self,
        name: str,
        import_name: str,
        tag: t.Optional[t.Union[str, dict]] = None,
        enable_openapi: bool = True,
        static_folder: t.Optional[str] = None,
        static_url_path: t.Optional[str] = None,
        template_folder: t.Optional[str] = None,
        url_prefix: t.Optional[str] = None,
        subdomain: t.Optional[str] = None,
        url_defaults: t.Optional[dict] = None,
        root_path: t.Optional[str] = None,
        cli_group: t.Union[t.Optional[str]] = _sentinel  # type: ignore
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
            enable_openapi: If `False`, will disable OpenAPI support for the
                current blueprint.

        Other keyword arguments are directly passed to `flask.Blueprint`.
        """
        super().__init__(
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
        self.enable_openapi = enable_openapi
