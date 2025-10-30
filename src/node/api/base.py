from abc import ABC, abstractmethod
from typing import AsyncIterator, List

from node.api.serializers.block import BlockSerializer
from node.api.serializers.health import HealthSerializer


class NodeApi(ABC):
    @abstractmethod
    async def get_health(self) -> HealthSerializer:
        pass

    @abstractmethod
    async def get_blocks(self, **kwargs) -> List[BlockSerializer]:
        pass

    @abstractmethod
    async def get_blocks_stream(self) -> AsyncIterator[List[BlockSerializer]]:
        pass
