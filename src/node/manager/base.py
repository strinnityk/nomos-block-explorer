from abc import ABC, abstractmethod


class NodeManager(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
