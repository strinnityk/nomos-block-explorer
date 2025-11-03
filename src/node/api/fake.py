from asyncio import sleep
from random import choices, random
from typing import TYPE_CHECKING, AsyncIterator, List

from rusty_results import Some

from node.api.base import NodeApi
from node.api.serializers.block import BlockSerializer
from node.api.serializers.health import HealthSerializer

if TYPE_CHECKING:
    from core.app import NBESettings


def get_weighted_amount() -> int:
    items = [1, 2, 3]
    weights = [0.6, 0.3, 0.1]
    return choices(items, weights=weights, k=1)[0]


class FakeNodeApi(NodeApi):
    def __init__(self, _settings: "NBESettings"):
        self.current_slot: int = 0

    async def get_health(self) -> HealthSerializer:
        if random() < 0.1:
            return HealthSerializer.from_unhealthy()
        else:
            return HealthSerializer.from_healthy()

    async def get_blocks(self, **kwargs) -> List[BlockSerializer]:
        n = get_weighted_amount()
        assert n >= 1
        blocks = [BlockSerializer.from_random() for _ in range(n)]
        self.current_slot = max(blocks, key=lambda block: block.slot).slot
        return blocks

    async def get_blocks_stream(self) -> AsyncIterator[BlockSerializer]:
        while True:
            yield BlockSerializer.from_random(slot=Some(self.current_slot))
            self.current_slot += 1
            await sleep(3)
