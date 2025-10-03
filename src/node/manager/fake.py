from node.manager.base import NodeManager


class FakeNodeManager(NodeManager):
    async def start(self):
        pass

    async def stop(self):
        pass
