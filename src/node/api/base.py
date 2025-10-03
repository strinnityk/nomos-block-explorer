from abc import ABC, abstractmethod
from typing import List

from node.models.blocks import Block
from node.models.health import Health
from node.models.transactions import Transaction


class NodeApi(ABC):
    @abstractmethod
    async def get_health_check(self) -> Health:
        pass

    @abstractmethod
    async def get_transactions(self) -> List[Transaction]:
        pass

    @abstractmethod
    async def get_blocks(self) -> List[Block]:
        pass
