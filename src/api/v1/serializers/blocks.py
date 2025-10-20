from typing import List, Self

from core.models import NbeSchema
from node.models.blocks import Block, Header
from node.models.transactions import Transaction


class BlockRead(NbeSchema):
    id: int
    slot: int
    header: Header
    transactions: List[Transaction]

    @classmethod
    def from_block(cls, block: Block) -> Self:
        return cls(
            id=block.id,
            slot=block.header.slot,
            header=block.header,
            transactions=block.transactions,
        )
