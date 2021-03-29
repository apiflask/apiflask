from typing import Optional, Union
from flask import Blueprint

from .utils import route_shortcuts
from .utils import _sentinel


@route_shortcuts
class APIBlueprint(Blueprint):
    """Flask's Blueprint with some API support.

    .. versionadded:: 0.2.0
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
