from typing import TYPE_CHECKING

from node.manager.base import NodeManager

if TYPE_CHECKING:
    from core.app import NBESettings


class NoopNodeManager(NodeManager):
    def __init__(self, _settings: "NBESettings"):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass
