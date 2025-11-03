from typing import TYPE_CHECKING

from node.api.base import NodeApi
from node.api.fake import FakeNodeApi
from node.api.http import HttpNodeApi

if TYPE_CHECKING:
    from core.app import NBESettings


def build_node_api(settings: "NBESettings") -> NodeApi:
    match settings.node_api:
        case "http":
            return HttpNodeApi(settings)
        case "fake":
            return FakeNodeApi(settings)
        case _:
            raise ValueError(f"Unknown API name: {settings.node_api}. Available options are: 'api', 'fake'.")
