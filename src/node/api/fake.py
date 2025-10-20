from random import choices, random
from typing import AsyncIterator, List

from node.api.base import NodeApi
from node.models.blocks import Block
from node.models.health import Health
from node.models.transactions import Transaction


def get_weighted_amount() -> int:
    items = [1, 2, 3]
    weights = [0.6, 0.3, 0.1]
    return choices(items, weights=weights, k=1)[0]


class FakeNodeApi(NodeApi):
    async def get_health_check(self) -> Health:
        if random() < 0.1:
            return Health.from_unhealthy()
        else:
            return Health.from_healthy()

    async def get_blocks(self) -> List[Block]:
        return [Block.from_random() for _ in range(1)]

    async def get_blocks_stream(self) -> AsyncIterator[Block]:
        while True:
            yield Block.from_random()
